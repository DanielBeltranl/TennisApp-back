
from django.urls import path, include
from rest_framework import routers
from apiusuario import views
from rest_framework_simplejwt.views import TokenRefreshView

router = routers.DefaultRouter()
router.register(r'usuarios', views.UsuarioViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.TokenObtainPairViewPersonalizado.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # ✅ Sin 'views.'
]