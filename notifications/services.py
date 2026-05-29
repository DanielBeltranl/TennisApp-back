from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Notificacion, TipoNotificacion


def crear_notificacion(usuario, tipo, payload):
    noti = Notificacion.objects.create(usuario=usuario, tipo=tipo, payload=payload)

    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            f'notifications_{usuario.id}',
            {
                'type': 'send_notification',
                'data': {
                    'id': str(noti.id),
                    'tipo': noti.tipo,
                    'payload': noti.payload,
                    'created_at': noti.created_at.isoformat(),
                },
            }
        )
