from django.urls import path
from .views import NotificacionListView, MarcarLeidaView, MarcarTodasLeidasView

urlpatterns = [
    path('', NotificacionListView.as_view(), name='notificaciones-list'),
    path('<uuid:pk>/leer/', MarcarLeidaView.as_view(), name='notificacion-leer'),
    path('leer-todas/', MarcarTodasLeidasView.as_view(), name='notificaciones-leer-todas'),
]
