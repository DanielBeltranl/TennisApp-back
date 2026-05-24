from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

from apiusuario.views import TokenObtainPairViewPersonalizado

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apiusuario.urls')),
    path('api/matches/', include('matches.urls')),
    path('api/', include('statistics.urls')),
    path('api/', include('friendship.urls')),
    path('api/coaching/', include('coaching.urls')),
    path('api/login/', TokenObtainPairViewPersonalizado.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]