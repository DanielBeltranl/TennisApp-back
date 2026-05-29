from django.urls import path
from .views import (
    EntrenadorSearchView,
    EnviarSolicitudView,
    SolicitudesEnviadasView,
    SolicitudesRecibidasView,
    AceptarSolicitudView,
    RechazarSolicitudView,
    DashboardEntrenadorView,
    JugadoresEntrenadorView,
    ActualizarNivelJugadorView,
    JugadorSearchView,
    PartidosInvitadosJugadoresView,
    HistorialJugadoresView,
)

urlpatterns = [
    path('entrenadores/', EntrenadorSearchView.as_view(), name='entrenador-search'),
    path('jugadores/', JugadoresEntrenadorView.as_view(), name='jugadores-entrenador'),
    path('jugadores/<int:pk>/nivel/', ActualizarNivelJugadorView.as_view(), name='jugador-nivel'),
    path('jugadores/buscar/', JugadorSearchView.as_view(), name='jugador-search'),
    path('solicitudes/', EnviarSolicitudView.as_view(), name='solicitud-enviar'),
    path('solicitudes/enviadas/', SolicitudesEnviadasView.as_view(), name='solicitudes-enviadas'),
    path('solicitudes/recibidas/', SolicitudesRecibidasView.as_view(), name='solicitudes-recibidas'),
    path('solicitudes/<int:pk>/aceptar/', AceptarSolicitudView.as_view(), name='solicitud-aceptar'),
    path('solicitudes/<int:pk>/rechazar/', RechazarSolicitudView.as_view(), name='solicitud-rechazar'),
    path('dashboard/', DashboardEntrenadorView.as_view(), name='dashboard-entrenador'),
    path('partidos-invitados/', PartidosInvitadosJugadoresView.as_view(), name='partidos-invitados-jugadores'),
    path('historial/', HistorialJugadoresView.as_view(), name='historial-jugadores'),
]
