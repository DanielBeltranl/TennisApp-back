from django.urls import path
from .views import MatchStatsView, GlobalStatsView, LiveMatchStatsView

urlpatterns = [
    path('statistics/match/<uuid:pk>/', MatchStatsView.as_view(), name='match-stats'),
    path('statistics/match/<uuid:pk>/live/', LiveMatchStatsView.as_view(), name='live-match-stats'),
    path('statistics/global/', GlobalStatsView.as_view(), name='global-stats'),
]
