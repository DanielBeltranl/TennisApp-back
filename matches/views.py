from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Player, MatchData, MatchScore, MatchSet, MatchPoint, MatchGame
from .serializer import (
    PlayerSerializer,
    MatchDataSerializer,
    MatchScoreSerializer,
    MatchSetSerializer,
    MatchPointSerializer,
    MatchGameSerializer
)


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [IsAuthenticated]


class MatchDataViewSet(viewsets.ModelViewSet):
    queryset = MatchData.objects.all().prefetch_related('player_1', 'player_2', 'match_scores')
    serializer_class = MatchDataSerializer
    permission_classes = [IsAuthenticated]


class MatchScoreViewSet(viewsets.ModelViewSet):
    queryset = MatchScore.objects.all().prefetch_related('match_sets', 'match_points', 'winner_id')
    serializer_class = MatchScoreSerializer
    permission_classes = [IsAuthenticated]


class MatchSetViewSet(viewsets.ModelViewSet):
    queryset = MatchSet.objects.all().select_related('winner_id')
    serializer_class = MatchSetSerializer
    permission_classes = [IsAuthenticated]


class MatchPointViewSet(viewsets.ModelViewSet):
    queryset = MatchPoint.objects.all().select_related('id_player_1', 'id_player_2', 'winner_id')
    serializer_class = MatchPointSerializer
    permission_classes = [IsAuthenticated]


class MatchGameViewSet(viewsets.ModelViewSet):
    queryset = MatchGame.objects.all().select_related('winner_id')
    serializer_class = MatchGameSerializer
    permission_classes = [IsAuthenticated]
