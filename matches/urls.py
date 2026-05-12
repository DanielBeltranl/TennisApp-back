from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PlayerViewSet,
    MatchDataViewSet,
    MatchScoreViewSet,
    MatchSetViewSet,
    MatchPointViewSet,
    MatchGameViewSet
)

router = DefaultRouter()
router.register(r'players', PlayerViewSet, basename='player')
router.register(r'match-data', MatchDataViewSet, basename='match-data')
router.register(r'match-scores', MatchScoreViewSet, basename='match-score')
router.register(r'match-sets', MatchSetViewSet, basename='match-set')
router.register(r'match-points', MatchPointViewSet, basename='match-point')
router.register(r'match-games', MatchGameViewSet, basename='match-game')

urlpatterns = [
    path('', include(router.urls)),
]
