from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import MatchData, MatchScore, MatchSet, MatchPoint, MatchGame
from .serializer import (
    MatchDataSerializer,
    MatchScoreSerializer,
    MatchSetSerializer,
    MatchPointSerializer,
    MatchGameSerializer,
)


class MatchDataViewSet(viewsets.ModelViewSet):
    queryset = MatchData.objects.all().select_related('player_1', 'player_2')
    serializer_class = MatchDataSerializer
    permission_classes = [IsAuthenticated]


class MatchScoreViewSet(viewsets.ModelViewSet):
    queryset = MatchScore.objects.all().select_related('winner_id', 'id_partido')
    serializer_class = MatchScoreSerializer
    permission_classes = [IsAuthenticated]


class MatchSetViewSet(viewsets.ModelViewSet):
    queryset = MatchSet.objects.all().select_related('winner_id', 'id_match_score')
    serializer_class = MatchSetSerializer
    permission_classes = [IsAuthenticated]


class MatchPointViewSet(viewsets.ModelViewSet):
    queryset = MatchPoint.objects.all().select_related('id_player_1', 'id_player_2', 'winner_id', 'id_game')
    serializer_class = MatchPointSerializer
    permission_classes = [IsAuthenticated]


class MatchGameViewSet(viewsets.ModelViewSet):
    queryset = MatchGame.objects.all().select_related('winner_id', 'id_set')
    serializer_class = MatchGameSerializer
    permission_classes = [IsAuthenticated]
