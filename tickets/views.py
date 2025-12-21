from __future__ import annotations

from rest_framework import permissions, viewsets

from .models import Ticket
from .serializers import TicketCreateSerializer, TicketSerializer, TicketSupportUpdateSerializer


def _is_support(user) -> bool:
    return user.is_authenticated and (user.is_superuser or user.roles.filter(name__in=['support', 'admin']).exists())


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all().order_by('-created_at')
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if _is_support(user):
            return super().get_queryset()
        return super().get_queryset().filter(user=user)

    def get_serializer_class(self):
        if self.action == 'create':
            return TicketCreateSerializer
        if self.action in ['update', 'partial_update'] and _is_support(self.request.user):
            return TicketSupportUpdateSerializer
        return TicketSerializer

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        # Non-support users can only update their own ticket title/message; however assignment says
        # "users can change their tickets" but customer cannot answer. We'll just allow support to set response.
        if _is_support(self.request.user):
            serializer.save()
            return

        # For regular users, disallow changing response/status
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        # Only support/admin can delete tickets
        if not _is_support(request.user):
            self.permission_denied(request, message='Only support/admin can delete tickets')
        return super().destroy(request, *args, **kwargs)
