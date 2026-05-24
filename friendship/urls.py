from django.urls import path
from .views import (
    PlayerSearchView,
    SendFriendRequestView,
    AcceptFriendRequestView,
    RejectFriendRequestView,
    PendingRequestsView,
    SentPendingRequestsView,
    FriendListView,
    RemoveFriendView,
)

urlpatterns = [
    path('players/search/', PlayerSearchView.as_view(), name='player-search'),
    path('friends/', FriendListView.as_view(), name='friend-list'),
    path('friends/request/', SendFriendRequestView.as_view(), name='friend-request-send'),
    path('friends/requests/', PendingRequestsView.as_view(), name='friend-requests-pending'),
    path('friends/requests/sent/', SentPendingRequestsView.as_view(), name='friend-requests-sent'),
    path('friends/request/<int:pk>/accept/', AcceptFriendRequestView.as_view(), name='friend-request-accept'),
    path('friends/request/<int:pk>/reject/', RejectFriendRequestView.as_view(), name='friend-request-reject'),
    path('friends/<int:pk>/', RemoveFriendView.as_view(), name='friend-remove'),
]
