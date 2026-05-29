import uuid
from django.db import models
from django.contrib.auth import get_user_model

Usuario = get_user_model()


class TipoNotificacion(models.TextChoices):
    SOLICITUD_AMISTAD    = 'solicitud_amistad'
    SOLICITUD_ENTRENADOR = 'solicitud_entrenador'
    SOLICITUD_ACEPTADA   = 'solicitud_aceptada'
    SOLICITUD_RECHAZADA  = 'solicitud_rechazada'
    PARTIDO_AGENDADO     = 'partido_agendado'
    PARTIDO_ACEPTADO     = 'partido_aceptado'
    PARTIDO_RECHAZADO    = 'partido_rechazado'
    PARTIDO_INICIADO     = 'partido_iniciado'
    PARTIDO_FINALIZADO   = 'partido_finalizado'


class Notificacion(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario    = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='notificaciones')
    tipo       = models.CharField(max_length=30, choices=TipoNotificacion.choices)
    payload    = models.JSONField(default=dict)
    leida      = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
