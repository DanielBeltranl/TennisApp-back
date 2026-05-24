from django.conf import settings
from django.db import models


class EstadoSolicitud(models.TextChoices):
    pendiente = 'PENDIENTE'
    aceptada = 'ACEPTADA'
    rechazada = 'RECHAZADA'


class SolicitudAsociacion(models.Model):
    jugador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='solicitudes_enviadas',
    )
    entrenador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='solicitudes_recibidas',
    )
    status = models.CharField(
        max_length=20,
        choices=EstadoSolicitud.choices,
        default=EstadoSolicitud.pendiente,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'solicitud_asociacion'
        unique_together = ('jugador', 'entrenador')

    def __str__(self):
        return f"{self.jugador} → {self.entrenador} [{self.status}]"
