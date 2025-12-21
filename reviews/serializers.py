from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

from ads.models import Advertisement
from .models import Review

User = get_user_model()


class ReviewSerializer(serializers.ModelSerializer):
    author_id = serializers.IntegerField(read_only=True)
    contractor_id = serializers.IntegerField(read_only=True)
    advertisement_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'advertisement_id', 'contractor_id', 'author_id', 'rating', 'comment', 'created_at']
        read_only_fields = ['created_at', 'author_id', 'contractor_id', 'advertisement_id']


class CreateReviewSerializer(serializers.Serializer):
    advertisement_id = serializers.IntegerField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField()

    def validate_advertisement_id(self, ad_id: int) -> int:
        ad = Advertisement.objects.select_related('contractor', 'customer').filter(id=ad_id).first()
        if not ad:
            raise serializers.ValidationError('Advertisement not found')
        if ad.status != Advertisement.STATUS_DONE:
            raise serializers.ValidationError('Advertisement is not DONE')
        if not ad.contractor_id:
            raise serializers.ValidationError('Advertisement has no contractor')
        request = self.context['request']
        if ad.customer_id != request.user.id:
            raise serializers.ValidationError('Only the ad owner can review')
        if hasattr(ad, 'review'):
            raise serializers.ValidationError('Review already exists')
        return ad_id

    def create(self, validated_data):
        request = self.context['request']
        ad = Advertisement.objects.get(id=validated_data['advertisement_id'])
        return Review.objects.create(
            advertisement=ad,
            contractor_id=ad.contractor_id,
            author=request.user,
            rating=validated_data['rating'],
            comment=validated_data['comment'],
        )
