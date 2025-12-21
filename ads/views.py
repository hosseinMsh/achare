from __future__ import annotations

from django.db.models import Q
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Advertisement, JobRequest
from .permissions import CanViewAdvertisement, IsContractor, IsCustomer
from .serializers import (
    AdvertisementCreateSerializer,
    AdvertisementSerializer,
    AssignContractorSerializer,
    ContractorMarkDoneSerializer,
    CreateJobRequestSerializer,
    CustomerCancelAdSerializer,
    CustomerConfirmDoneSerializer,
    JobRequestSerializer,
)


class AdvertisementViewSet(viewsets.ModelViewSet):
    """CRUD for ads with access control.

    Visibility rules:
    - customer: own ads
    - contractor: OPEN ads + assigned ads
    - support/admin: all
    """

    queryset = Advertisement.objects.all().order_by('-created_at')
    serializer_class = AdvertisementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.IsAuthenticated(), IsCustomer()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return AdvertisementCreateSerializer
        return AdvertisementSerializer

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()

        if user.is_superuser or user.roles.filter(name__in=['admin', 'support']).exists():
            return qs

        # customer: only own ads
        if user.roles.filter(name='customer').exists():
            return qs.filter(customer=user)

        # contractor: OPEN ads + assigned-to-me
        if user.roles.filter(name='contractor').exists():
            return qs.filter(Q(status=Advertisement.STATUS_OPEN) | Q(contractor=user))

        # default: nothing
        return qs.none()

    def get_object(self):
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj

    def get_object_permissions(self):
        return [CanViewAdvertisement()]

    def check_object_permissions(self, request, obj):
        # Use explicit object permission for retrieve/update/delete
        perm = CanViewAdvertisement()
        if not perm.has_object_permission(request, self, obj):
            self.permission_denied(request, message='Not allowed')

    def perform_update(self, serializer):
        # Only allow customer to update own OPEN ads (basic rule)
        ad = self.get_object()
        user = self.request.user
        if not user.is_superuser and not user.roles.filter(name__in=['admin', 'support']).exists():
            if ad.customer_id != user.id:
                raise permissions.PermissionDenied('Only owner can update')
            if ad.status != Advertisement.STATUS_OPEN:
                raise permissions.PermissionDenied('Only OPEN ads can be updated')
        serializer.save()

    def perform_destroy(self, instance):
        # Safer to disallow deletes for non-admin roles.
        user = self.request.user
        if not (user.is_superuser or user.roles.filter(name__in=['admin', 'support']).exists()):
            raise permissions.PermissionDenied('Deleting ads is not allowed')
        instance.delete()

    @action(detail=False, methods=['post'], url_path='assign')
    def assign_contractor(self, request):
        """Customer selects a contractor from job requests."""
        if not request.user.roles.filter(name='customer').exists() and not request.user.is_superuser:
            return Response({'detail': 'Only customers can assign'}, status=status.HTTP_403_FORBIDDEN)
        serializer = AssignContractorSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        ad = serializer.save()
        return Response(AdvertisementSerializer(ad).data)

    @action(detail=False, methods=['post'], url_path='contractor-done')
    def contractor_done(self, request):
        if not request.user.roles.filter(name='contractor').exists() and not request.user.is_superuser:
            return Response({'detail': 'Only contractors can mark done'}, status=status.HTTP_403_FORBIDDEN)
        serializer = ContractorMarkDoneSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        ad = serializer.save()
        return Response(AdvertisementSerializer(ad).data)

    @action(detail=False, methods=['post'], url_path='confirm-done')
    def confirm_done(self, request):
        if not request.user.roles.filter(name='customer').exists() and not request.user.is_superuser:
            return Response({'detail': 'Only customers can confirm'}, status=status.HTTP_403_FORBIDDEN)
        serializer = CustomerConfirmDoneSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        ad = serializer.save()
        return Response(AdvertisementSerializer(ad).data)

    @action(detail=False, methods=['post'], url_path='cancel')
    def cancel(self, request):
        if not request.user.roles.filter(name='customer').exists() and not request.user.is_superuser:
            return Response({'detail': 'Only customers can cancel'}, status=status.HTTP_403_FORBIDDEN)
        serializer = CustomerCancelAdSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        ad = serializer.save()
        return Response(AdvertisementSerializer(ad).data)


class JobRequestViewSet(viewsets.ModelViewSet):
    """Contractors create/cancel job requests."""

    queryset = JobRequest.objects.select_related('advertisement').order_by('-created_at')
    serializer_class = JobRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.is_superuser or user.roles.filter(name__in=['admin', 'support']).exists():
            return qs

        # contractor: see own requests
        if user.roles.filter(name='contractor').exists():
            return qs.filter(contractor=user)

        # customer: see requests for own ads
        if user.roles.filter(name='customer').exists():
            return qs.filter(advertisement__customer=user)

        return qs.none()

    def create(self, request, *args, **kwargs):
        if not request.user.roles.filter(name='contractor').exists() and not request.user.is_superuser:
            return Response({'detail': 'Only contractors can request jobs'}, status=status.HTTP_403_FORBIDDEN)
        serializer = CreateJobRequestSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        obj = serializer.create(serializer.validated_data)
        return Response(JobRequestSerializer(obj).data, status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        # Only allow toggling is_active by request owner (cancel).
        jr = self.get_object()
        user = self.request.user
        if not (user.is_superuser or user.roles.filter(name__in=['admin', 'support']).exists()):
            if jr.contractor_id != user.id:
                raise permissions.PermissionDenied('Only request owner can modify')
        serializer.save()

    def perform_destroy(self, instance):
        # Disallow deletes; use is_active=False instead.
        raise permissions.PermissionDenied('Deleting job requests is not allowed')

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        jr = self.get_object()
        if jr.contractor_id != request.user.id and not request.user.is_superuser:
            return Response({'detail': 'Only request owner can cancel'}, status=status.HTTP_403_FORBIDDEN)
        jr.is_active = False
        jr.save(update_fields=['is_active'])
        return Response(JobRequestSerializer(jr).data)
