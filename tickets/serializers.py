from __future__ import annotations

from rest_framework import serializers

from .models import Ticket


class TicketSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'user_id', 'title', 'message', 'response', 'status', 'created_at']
        read_only_fields = ['response', 'status', 'created_at', 'user_id']


class TicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['id', 'title', 'message']

    def create(self, validated_data):
        request = self.context['request']
        return Ticket.objects.create(user=request.user, **validated_data)


class TicketSupportUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['response', 'status']
