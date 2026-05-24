from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from apiusuario.models import RolUsuario
from apiusuario.permissions import EsJugador, EsEntrenador
from matches.models import MatchData, MatchState
from .models import SolicitudAsociacion, EstadoSolicitud
from .serializers import (
    EntrenadorResumenSerializer,
    SolicitudAsociacionSerializer,
    EnviarSolicitudSerializer,
    AceptarSolicitudSerializer,
)

Usuario = get_user_model()


class EntrenadorSearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        term = request.query_params.get('q', '').strip()
        if not term:
            return Response([])

        entrenadores = Usuario.objects.filter(
            rol=RolUsuario.entrenador,
            is_active=True,
        ).filter(
            nombre__icontains=term,
        ) | Usuario.objects.filter(
            rol=RolUsuario.entrenador,
            is_active=True,
            apellidoPaterno__icontains=term,
        ) | Usuario.objects.filter(
            rol=RolUsuario.entrenador,
            is_active=True,
            correo__icontains=term,
        )

        return Response(EntrenadorResumenSerializer(entrenadores.distinct()[:15], many=True).data)


class EnviarSolicitudView(APIView):
    permission_classes = [IsAuthenticated, EsJugador]

    def post(self, request):
        serializer = EnviarSolicitudSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        solicitud = serializer.save()
        return Response(SolicitudAsociacionSerializer(solicitud).data, status=status.HTTP_201_CREATED)


class SolicitudesEnviadasView(APIView):
    permission_classes = [IsAuthenticated, EsJugador]

    def get(self, request):
        solicitudes = SolicitudAsociacion.objects.filter(
            jugador=request.user,
        ).select_related('jugador', 'entrenador').order_by('-created_at')

        return Response(SolicitudAsociacionSerializer(solicitudes, many=True).data)


class SolicitudesRecibidasView(APIView):
    permission_classes = [IsAuthenticated, EsEntrenador]

    def get(self, request):
        solicitudes = SolicitudAsociacion.objects.filter(
            entrenador=request.user,
            status=EstadoSolicitud.pendiente,
        ).select_related('jugador', 'entrenador').order_by('-created_at')

        return Response(SolicitudAsociacionSerializer(solicitudes, many=True).data)


class AceptarSolicitudView(APIView):
    permission_classes = [IsAuthenticated, EsEntrenador]

    def patch(self, request, pk):
        try:
            solicitud = SolicitudAsociacion.objects.select_related('jugador').get(
                id=pk,
                entrenador=request.user,
                status=EstadoSolicitud.pendiente,
            )
        except SolicitudAsociacion.DoesNotExist:
            return Response({'error': 'Solicitud no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AceptarSolicitudSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            jugador = solicitud.jugador
            jugador.nivelUsuario = serializer.validated_data['nivel']
            jugador.entrenador = request.user
            jugador.save(update_fields=['nivelUsuario', 'entrenador'])

            solicitud.status = EstadoSolicitud.aceptada
            solicitud.save(update_fields=['status', 'updated_at'])

        return Response({
            'id': solicitud.id,
            'jugador': EntrenadorResumenSerializer(solicitud.jugador).data,
            'status': solicitud.status,
            'nivel_asignado': jugador.nivelUsuario,
        })


class RechazarSolicitudView(APIView):
    permission_classes = [IsAuthenticated, EsEntrenador]

    def patch(self, request, pk):
        try:
            solicitud = SolicitudAsociacion.objects.get(
                id=pk,
                entrenador=request.user,
                status=EstadoSolicitud.pendiente,
            )
        except SolicitudAsociacion.DoesNotExist:
            return Response({'error': 'Solicitud no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        solicitud.status = EstadoSolicitud.rechazada
        solicitud.save(update_fields=['status', 'updated_at'])

        return Response({'id': solicitud.id, 'status': solicitud.status})


class DashboardEntrenadorView(APIView):
    permission_classes = [IsAuthenticated, EsEntrenador]

    def get(self, request):
        jugadores_ids = set(
            Usuario.objects.filter(entrenador=request.user).values_list('id', flat=True)
        )

        if not jugadores_ids:
            return Response({'partidos': []})

        matches = (
            MatchData.objects.filter(
                Q(id_player_creator_id__in=jugadores_ids) | Q(id_player_invited_id__in=jugadores_ids),
                match_state=MatchState.FINALIZADA,
            )
            .select_related('id_player_creator', 'id_player_invited', 'match_score')
            .prefetch_related('match_score__match_sets')
            .order_by('-updated_at')[:5]
        )

        return Response({'partidos': [self._serializar(m, jugadores_ids) for m in matches]})

    def _serializar(self, match, jugadores_ids):
        jugador_es_creator = match.id_player_creator_id in jugadores_ids
        jugador = match.id_player_creator if jugador_es_creator else match.id_player_invited

        if jugador_es_creator:
            oponente_nombre = match.id_player_invited.nombre if match.id_player_invited else match.guest_name or ''
            oponente_apellido = match.id_player_invited.apellidoPaterno if match.id_player_invited else ''
            es_invitado = match.id_player_invited_id is None
        else:
            oponente_nombre = match.id_player_creator.nombre
            oponente_apellido = match.id_player_creator.apellidoPaterno
            es_invitado = False

        sets_data = []
        marcador_jugador = 0
        marcador_oponente = 0
        duracion = None

        try:
            score = match.match_score
            duracion = score.duration
            sets = sorted(score.match_sets.all(), key=lambda s: s.created_at)

            for i, s in enumerate(sets):
                jugador_score = s.score_p1 if jugador_es_creator else s.score_p2
                oponente_score = s.score_p2 if jugador_es_creator else s.score_p1

                jugador_gano_set = (
                    s.winner_id_id == jugador.id
                    if s.winner_id_id is not None
                    else (not jugador_es_creator and s.duration is not None)
                )

                if jugador_gano_set:
                    marcador_jugador += 1
                elif s.duration is not None:
                    marcador_oponente += 1

                sets_data.append({
                    'set_number': i + 1,
                    'jugador': jugador_score,
                    'oponente': oponente_score,
                })
        except Exception:
            pass

        return {
            'id_match': match.id_match,
            'jugador': {
                'id': jugador.id,
                'nombre': jugador.nombre,
                'apellidoPaterno': jugador.apellidoPaterno,
                'nivelUsuario': jugador.nivelUsuario,
            },
            'oponente': {
                'nombre': oponente_nombre,
                'apellidoPaterno': oponente_apellido,
                'es_invitado': es_invitado,
            },
            'marcador_global': {'jugador': marcador_jugador, 'oponente': marcador_oponente},
            'sets': sets_data,
            'duration': duracion,
            'location': match.location,
            'surface': match.surface,
            'created_at': match.created_at,
        }
