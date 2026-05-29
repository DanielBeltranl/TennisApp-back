from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from matches.models import MatchData, MatchScore, MatchPoint, MatchState
from .calculators import get_match_stats, get_global_stats, get_live_stats, get_live_stats_guest

Usuario = get_user_model()


def _resolve_player_for_match(request, match):
    """
    Returns (player, error_response).
    - If jugador: must be a participant.
    - If entrenador: finds which participant belongs to them.
    """
    is_entrenador = request.auth.get('rol') == 'Entrenador'

    if not is_entrenador:
        if request.user.id not in {match.id_local_player_id, match.id_invited_player_id}:
            return None, Response({'error': 'No sos participante de este partido.'}, status=status.HTTP_403_FORBIDDEN)
        return request.user, None

    player = None
    if match.id_local_player and getattr(match.id_local_player, 'entrenador_id', None) == request.user.id:
        player = match.id_local_player
    elif match.id_invited_player and getattr(match.id_invited_player, 'entrenador_id', None) == request.user.id:
        player = match.id_invited_player

    if not player:
        return None, Response({'error': 'Ningún jugador de este partido pertenece a tu equipo.'}, status=status.HTTP_403_FORBIDDEN)

    return player, None


class MatchStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            match = MatchData.objects.select_related(
                'id_local_player', 'id_invited_player',
                'id_local_player__entrenador', 'id_invited_player__entrenador',
                'match_score'
            ).get(id_match=pk)
        except MatchData.DoesNotExist:
            return Response({'error': 'Partido no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        if match.match_state != MatchState.FINALIZADA:
            return Response({'error': 'El partido no está finalizado.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            match_score = match.match_score
        except MatchScore.DoesNotExist:
            return Response({'error': 'Sin marcador registrado.'}, status=status.HTTP_400_BAD_REQUEST)

        points = list(
            MatchPoint.objects.filter(
                id_game__id_set__id_match_score__id_partido=match
            ).select_related('winner_id', 'is_serving', 'id_game').order_by('created_at')
        )

        is_entrenador = request.auth.get('rol') == 'Entrenador'

        if is_entrenador:
            players = []
            if match.id_local_player and getattr(match.id_local_player, 'entrenador_id', None) == request.user.id:
                players.append(match.id_local_player)
            if match.id_invited_player and getattr(match.id_invited_player, 'entrenador_id', None) == request.user.id:
                players.append(match.id_invited_player)

            if not players:
                return Response({'error': 'Ningún jugador de este partido pertenece a tu equipo.'}, status=status.HTTP_403_FORBIDDEN)

            return Response([
                {
                    'player_id': p.id,
                    'nombre': p.nombre,
                    'apellidoPaterno': p.apellidoPaterno,
                    **get_match_stats(points, p.id, match_score, p.nivelUsuario or 'Amateur', p.sexo or 'Masculino', match.surface),
                }
                for p in players
            ])

        if request.user.id not in {match.id_local_player_id, match.id_invited_player_id}:
            return Response({'error': 'No sos participante de este partido.'}, status=status.HTTP_403_FORBIDDEN)

        player = request.user
        return Response(get_match_stats(points, player.id, match_score, player.nivelUsuario or 'Amateur', player.sexo or 'Masculino', match.surface))


class LiveMatchStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            match = MatchData.objects.select_related(
                'id_local_player', 'id_invited_player',
            ).get(id_match=pk)
        except MatchData.DoesNotExist:
            return Response({'error': 'Partido no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        is_participant = user.id in {match.id_local_player_id, match.id_invited_player_id}
        is_coach = match.id_entrenador_id == user.id
        if not is_participant and not is_coach:
            return Response({'error': 'No tenés acceso a este partido.'}, status=status.HTTP_403_FORBIDDEN)

        points = list(
            MatchPoint.objects.filter(
                id_game__id_set__id_match_score__id_partido=match
            ).select_related('winner_id', 'is_serving', 'id_game').order_by('created_at')
        )

        local = match.id_local_player
        invited = match.id_invited_player

        local_stats = {
            'player': {'id': local.id, 'nombre': local.nombre, 'apellidoPaterno': local.apellidoPaterno},
            **get_live_stats(points, local.id, local.nivelUsuario or 'Amateur', local.sexo or 'Masculino', match.surface),
        }

        if invited:
            opponent_stats = {
                'player': {'id': invited.id, 'nombre': invited.nombre, 'apellidoPaterno': invited.apellidoPaterno},
                **get_live_stats(points, invited.id, invited.nivelUsuario or 'Amateur', invited.sexo or 'Masculino', match.surface),
            }
        else:
            opponent_stats = {
                'player': {'id': None, 'nombre': match.guest_name or 'Invitado', 'apellidoPaterno': None},
                **get_live_stats_guest(points, local.id),
            }

        return Response([local_stats, opponent_stats])


class GlobalStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        is_entrenador = request.auth.get('rol') == 'Entrenador'

        if is_entrenador:
            player_id = request.query_params.get('player_id')
            if not player_id:
                return Response({'error': 'player_id es requerido para entrenadores.'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                player = Usuario.objects.get(id=player_id, entrenador=request.user, is_active=True)
            except Usuario.DoesNotExist:
                return Response({'error': 'Jugador no encontrado o no pertenece a tu equipo.'}, status=status.HTTP_403_FORBIDDEN)
        else:
            player = request.user

        matches = list(
            MatchData.objects.filter(
                Q(id_local_player=player) | Q(id_invited_player=player),
                match_state=MatchState.FINALIZADA,
            )
            .select_related('id_local_player', 'id_invited_player', 'match_score')
            .order_by('-updated_at')[:14]
        )

        if not matches:
            return Response({'message': 'Sin partidos finalizados aún.'}, status=status.HTTP_200_OK)

        nivel = player.nivelUsuario or 'Amateur'
        sexo  = player.sexo or 'Masculino'

        return Response(get_global_stats(matches, player.id, nivel, sexo))
