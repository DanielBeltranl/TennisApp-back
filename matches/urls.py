from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MatchDataViewSet,
    MatchScoreViewSet,
    MatchSetViewSet,
    MatchPointViewSet,
    MatchGameViewSet,
    ScheduleMatchView,
    AcceptMatchView,
    RejectMatchView,
    StartMatchView,
    PauseMatchView,
    ResumeMatchView,
    FinishMatchView,
    RecoverMatchView,
    MyCreatedMatchesView,
    MyInvitedMatchesView,
    RegisterPointView,
    UndoPointView,
    MatchSummaryView,
    MatchDetailView,
)

router = DefaultRouter()
router.register(r'match-data', MatchDataViewSet, basename='match-data')
router.register(r'match-scores', MatchScoreViewSet, basename='match-score')
router.register(r'match-sets', MatchSetViewSet, basename='match-set')
router.register(r'match-points', MatchPointViewSet, basename='match-point')
router.register(r'match-games', MatchGameViewSet, basename='match-game')

urlpatterns = [
    path('schedule/', ScheduleMatchView.as_view(), name='match-schedule'),
    path('my-created/', MyCreatedMatchesView.as_view(), name='my-created-matches'),
    path('summary/', MatchSummaryView.as_view(), name='match-summary'),
    path('my-invited/', MyInvitedMatchesView.as_view(), name='my-invited-matches'),
    path('<uuid:pk>/accept/', AcceptMatchView.as_view(), name='match-accept'),
    path('<uuid:pk>/reject/', RejectMatchView.as_view(), name='match-reject'),
    path('<uuid:pk>/start/', StartMatchView.as_view(), name='match-start'),
    path('<uuid:pk>/pause/', PauseMatchView.as_view(), name='match-pause'),
    path('<uuid:pk>/resume/', ResumeMatchView.as_view(), name='match-resume'),
    path('<uuid:pk>/finish/', FinishMatchView.as_view(), name='match-finish'),
    path('<uuid:pk>/recovery/', RecoverMatchView.as_view(), name='match-recovery'),
    path('<uuid:pk>/detail/', MatchDetailView.as_view(), name='match-detail'),
    path('<uuid:pk>/point/', RegisterPointView.as_view(), name='match-point-register'),
    path('<uuid:pk>/point/undo/', UndoPointView.as_view(), name='match-point-undo'),
    path('', include(router.urls)),
]
