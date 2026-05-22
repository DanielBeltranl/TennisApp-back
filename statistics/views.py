from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from matches.models import MatchData, MatchScore, MatchPoint, MatchState
from .calculators import get_match_stats, get_global_stats


class MatchStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            match = MatchData.objects.select_related(
                'id_player_creator', 'id_player_invited', 'match_score'
            ).get(id_match=pk)
        except MatchData.DoesNotExist:
            return Response({'error': 'Partido no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        if request.user.id not in {match.id_player_creator_id, match.id_player_invited_id}:
            return Response({'error': 'No sos participante de este partido.'}, status=status.HTTP_403_FORBIDDEN)

        if match.match_state != MatchState.FINALIZADA:
            return Response({'error': 'El partido no está finalizado.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            match_score = match.match_score
        except MatchScore.DoesNotExist:
            return Response({'error': 'Sin marcador registrado.'}, status=status.HTTP_400_BAD_REQUEST)

        points = list(
            MatchPoint.objects.filter(
                id_game__id_set__id_match_score__id_partido=match
            ).select_related('winner_id', 'is_serving').order_by('created_at')
        )

        nivel   = request.auth.get('nivelUsuario', 'Amateur')
        sexo    = request.auth.get('sexo', 'Masculino')
        surface = match.surface

        return Response(get_match_stats(points, request.user.id, match_score, nivel, sexo, surface))


class GlobalStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        matches = list(
            MatchData.objects.filter(
                Q(id_player_creator=request.user) | Q(id_player_invited=request.user),
                match_state=MatchState.FINALIZADA,
            )
            .select_related('id_player_creator', 'id_player_invited', 'match_score')
            .order_by('-updated_at')[:14]
        )

        if not matches:
            return Response({'message': 'Sin partidos finalizados aún.'}, status=status.HTTP_200_OK)

        nivel = request.auth.get('nivelUsuario', 'Amateur')
        sexo  = request.auth.get('sexo', 'Masculino')

        return Response(get_global_stats(matches, request.user.id, nivel, sexo))
