from __future__ import annotations

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from ads.models import Advertisement

User = settings.AUTH_USER_MODEL


class Review(models.Model):
    """Customer review about a contractor for a DONE ad."""

    advertisement = models.OneToOneField(Advertisement, on_delete=models.CASCADE, related_name='review')
    contractor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_written')

    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"review:{self.id} ad:{self.advertisement_id} rating:{self.rating}"
