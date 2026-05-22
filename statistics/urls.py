from django.urls import path
from .views import MatchStatsView, GlobalStatsView

urlpatterns = [
    path('statistics/match/<uuid:pk>/', MatchStatsView.as_view(), name='match-stats'),
    path('statistics/global/', GlobalStatsView.as_view(), name='global-stats'),
]
