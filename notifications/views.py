from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .models import Notificacion
from .serializers import NotificacionSerializer


class NotificacionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notis = Notificacion.objects.filter(usuario=request.user, leida=False)
        return Response(NotificacionSerializer(notis, many=True).data)


class MarcarLeidaView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            noti = Notificacion.objects.get(id=pk, usuario=request.user)
        except Notificacion.DoesNotExist:
            return Response({'error': 'Notificación no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        noti.leida = True
        noti.save(update_fields=['leida'])
        return Response({'id': str(noti.id), 'leida': True})


class MarcarTodasLeidasView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        Notificacion.objects.filter(usuario=request.user, leida=False).update(leida=True)
        return Response({'status': 'ok'})
