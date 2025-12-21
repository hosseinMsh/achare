from __future__ import annotations

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from .models import Advertisement, JobRequest

User = get_user_model()


class AdvertisementSerializer(serializers.ModelSerializer):
    customer_id = serializers.IntegerField(read_only=True)
    contractor_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Advertisement
        fields = [
            'id', 'title', 'description', 'category', 'status',
            'customer_id', 'contractor_id',
            'contractor_done', 'contractor_done_at',
            'created_at',
        ]
        read_only_fields = ['status', 'contractor_done', 'contractor_done_at', 'created_at', 'customer_id', 'contractor_id']


class AdvertisementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = ['id', 'title', 'description', 'category']

    def create(self, validated_data):
        request = self.context['request']
        return Advertisement.objects.create(customer=request.user, **validated_data)


class JobRequestSerializer(serializers.ModelSerializer):
    advertisement_id = serializers.IntegerField(read_only=True)
    contractor_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = JobRequest
        fields = ['id', 'advertisement_id', 'contractor_id', 'created_at', 'is_active']
        read_only_fields = ['created_at', 'advertisement_id', 'contractor_id']


class CreateJobRequestSerializer(serializers.Serializer):
    """Contractor requests an OPEN ad."""

    advertisement_id = serializers.IntegerField()

    def validate_advertisement_id(self, ad_id: int) -> int:
        ad = Advertisement.objects.filter(id=ad_id).first()
        if not ad:
            raise serializers.ValidationError('Advertisement not found')
        if ad.status != Advertisement.STATUS_OPEN:
            raise serializers.ValidationError('Advertisement is not OPEN')
        return ad_id

    def create(self, validated_data):
        request = self.context['request']
        ad = Advertisement.objects.get(id=validated_data['advertisement_id'])
        obj, _ = JobRequest.objects.get_or_create(advertisement=ad, contractor=request.user)
        obj.is_active = True
        obj.save(update_fields=['is_active'])
        return obj


class AssignContractorSerializer(serializers.Serializer):
    """Customer selects one contractor from active requests."""

    job_request_id = serializers.IntegerField()

    def validate_job_request_id(self, value: int) -> int:
        jr = JobRequest.objects.select_related('advertisement').filter(id=value).first()
        if not jr:
            raise serializers.ValidationError('Job request not found')
        ad = jr.advertisement
        if ad.status != Advertisement.STATUS_OPEN:
            raise serializers.ValidationError('Advertisement is not OPEN')
        if not jr.is_active:
            raise serializers.ValidationError('Job request is not active')
        return value

    def save(self, **kwargs):
        request = self.context['request']
        jr = JobRequest.objects.select_related('advertisement').get(id=self.validated_data['job_request_id'])
        ad = jr.advertisement
        if ad.customer_id != request.user.id:
            raise serializers.ValidationError('Only the ad owner can assign a contractor')

        ad.contractor = jr.contractor
        ad.status = Advertisement.STATUS_ASSIGNED
        ad.contractor_done = False
        ad.contractor_done_at = None
        ad.save(update_fields=['contractor', 'status', 'contractor_done', 'contractor_done_at'])

        # Deactivate all other requests (optional; keeps system tidy)
        JobRequest.objects.filter(advertisement=ad).exclude(id=jr.id).update(is_active=False)
        return ad


class ContractorMarkDoneSerializer(serializers.Serializer):
    """Assigned contractor announces completion (customer must confirm to finish)."""

    advertisement_id = serializers.IntegerField()

    def save(self, **kwargs):
        request = self.context['request']
        ad = Advertisement.objects.get(id=self.validated_data['advertisement_id'])
        if ad.status != Advertisement.STATUS_ASSIGNED:
            raise serializers.ValidationError('Advertisement is not ASSIGNED')
        if ad.contractor_id != request.user.id:
            raise serializers.ValidationError('Only the assigned contractor can mark done')
        ad.contractor_done = True
        ad.contractor_done_at = timezone.now()
        ad.save(update_fields=['contractor_done', 'contractor_done_at'])
        return ad


class CustomerConfirmDoneSerializer(serializers.Serializer):
    """Customer confirms completion and closes the ad."""

    advertisement_id = serializers.IntegerField()

    def save(self, **kwargs):
        request = self.context['request']
        ad = Advertisement.objects.get(id=self.validated_data['advertisement_id'])
        if ad.customer_id != request.user.id:
            raise serializers.ValidationError('Only the ad owner can confirm')
        if ad.status != Advertisement.STATUS_ASSIGNED:
            raise serializers.ValidationError('Advertisement is not ASSIGNED')
        if not ad.contractor_done:
            raise serializers.ValidationError('Contractor has not marked done yet')
        ad.status = Advertisement.STATUS_DONE
        ad.save(update_fields=['status'])
        return ad


class CustomerCancelAdSerializer(serializers.Serializer):
    advertisement_id = serializers.IntegerField()

    def save(self, **kwargs):
        request = self.context['request']
        ad = Advertisement.objects.get(id=self.validated_data['advertisement_id'])
        if ad.customer_id != request.user.id:
            raise serializers.ValidationError('Only the ad owner can cancel')
        if ad.status == Advertisement.STATUS_DONE:
            raise serializers.ValidationError('Cannot cancel a DONE ad')
        if ad.status == Advertisement.STATUS_CANCELED:
            return ad
        ad.status = Advertisement.STATUS_CANCELED
        ad.save(update_fields=['status'])
        return ad
