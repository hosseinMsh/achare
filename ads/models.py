from __future__ import annotations

from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL


class Advertisement(models.Model):
    """A service ad created by a customer."""

    STATUS_OPEN = 'open'
    STATUS_ASSIGNED = 'assigned'
    STATUS_DONE = 'done'
    STATUS_CANCELED = 'canceled'

    STATUS_CHOICES = [
        (STATUS_OPEN, 'Open'),
        (STATUS_ASSIGNED, 'Assigned'),
        (STATUS_DONE, 'Done'),
        (STATUS_CANCELED, 'Canceled'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=100)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_ads')
    contractor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='assigned_ads',
        null=True,
        blank=True,
    )

    # Used to show contractor's "finish" announcement before final customer confirmation.
    contractor_done = models.BooleanField(default=False)
    contractor_done_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.id} - {self.title}"


class JobRequest(models.Model):
    """A contractor's request to take an OPEN ad."""

    advertisement = models.ForeignKey(Advertisement, on_delete=models.CASCADE, related_name='requests')
    contractor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_requests')

    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['advertisement', 'contractor'], name='uniq_ad_contractor_request')
        ]

    def __str__(self) -> str:
        return f"req:{self.id} ad:{self.advertisement_id} contractor:{self.contractor_id}"
