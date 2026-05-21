from django.conf import settings
from django.db import models


class FriendshipStatus(models.TextChoices):
    PENDIENTE = 'PENDIENTE'
    ACEPTADO = 'ACEPTADO'


class Friendship(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='friendships_initiated'
    )
    friend = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='friendships_received'
    )
    status = models.CharField(
        max_length=20,
        choices=FriendshipStatus.choices,
        default=FriendshipStatus.PENDIENTE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'friendship'
        unique_together = ('user', 'friend')
