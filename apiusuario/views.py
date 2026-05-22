from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings
from rest_framework import permissions
from django.utils import timezone

from .serializer import UsuarioSerializer, TokenObtainPairSerializerPersonalizado
from .models import Usuario, TokenSession


class TokenObtainPairViewPersonalizado(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializerPersonalizado

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access_str = response.data.get('access')
            refresh_str = response.data.get('refresh')

            from rest_framework_simplejwt.tokens import AccessToken
            user_id = AccessToken(access_str).get('user_id')

            try:
                usuario = Usuario.objects.get(id=user_id)
                TokenSession.objects.filter(usuario=usuario, is_active=True).update(is_active=False)
                TokenSession.objects.create(
                    usuario=usuario,
                    access_token=access_str,
                    refresh_token=refresh_str,
                    expires_at=timezone.now() + api_settings.ACCESS_TOKEN_LIFETIME,
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
                    is_active=True,
                )
            except Usuario.DoesNotExist:
                pass

        return response


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def registro(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        usuario = serializer.save()

        refresh = RefreshToken.for_user(usuario)
        refresh['nivelUsuario'] = usuario.nivelUsuario
        refresh['sexo'] = usuario.sexo
        access_str = str(refresh.access_token)
        refresh_str = str(refresh)

        TokenSession.objects.create(
            usuario=usuario,
            access_token=access_str,
            refresh_token=refresh_str,
            expires_at=timezone.now() + api_settings.ACCESS_TOKEN_LIFETIME,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
            is_active=True,
        )

        return Response({
            'usuario': UsuarioSerializer(usuario).data,
            'access': access_str,
            'refresh': refresh_str,
            'mensaje': 'Usuario registrado exitosamente'
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def perfil(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def cambiar_password(self, request):
        usuario = request.user
        password_actual = request.data.get('password_actual')
        password_nuevo = request.data.get('password_nuevo')

        if not password_actual or not password_nuevo:
            return Response(
                {'error': 'Se requieren password_actual y password_nuevo'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not usuario.check_password(password_actual):
            return Response(
                {'error': 'La contraseña actual es incorrecta'},
                status=status.HTTP_400_BAD_REQUEST
            )

        usuario.set_password(password_nuevo)
        usuario.save()

        return Response({'mensaje': 'Contraseña cambiada exitosamente'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        try:
            session = TokenSession.objects.get(
                access_token=str(request.auth),
                usuario=request.user,
                is_active=True,
            )
            RefreshToken(session.refresh_token).blacklist()
            session.delete()
            return Response({'mensaje': 'Logout exitoso'}, status=status.HTTP_200_OK)
        except TokenSession.DoesNotExist:
            return Response(
                {'error': 'Sesión no encontrada o ya fue cerrada'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def sesiones_activas(self, request):
        sesiones = TokenSession.objects.filter(
            usuario=request.user,
            is_active=True
        ).values('id', 'created_at', 'expires_at', 'ip_address', 'user_agent')
        return Response({
            'sesiones': sesiones,
            'total': sesiones.count()
        }, status=status.HTTP_200_OK)
