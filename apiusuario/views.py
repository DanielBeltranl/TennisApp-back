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
    """
    Vista personalizada para obtener tokens JWT usando 'correo' en lugar de 'username'
    """
    serializer_class = TokenObtainPairSerializerPersonalizado


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def registro(self, request):
        """
        Endpoint para registrar un nuevo usuario
        Acepta: nombre, apellidoPaterno, apellidoMaterno, correo, password, edad, altura, peso, sexo, nivelUsuario
        Retorna: usuario creado + tokens JWT
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            usuario = serializer.save()
            
            # Generar tokens JWT para el usuario nuevo
            refresh = TokenObtainPairSerializerPersonalizado.get_token(usuario)
            access_token_str = str(refresh.access_token)
            refresh_token_str = str(refresh)
            
            # Validar que los tokens no existan para otro usuario (protección contra duplicados)
            if TokenSession.objects.filter(access_token=access_token_str, is_active=True).exclude(usuario=usuario).exists():
                return Response(
                    {'error': 'Error de generación de token. Intenta registrarte de nuevo.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Guardar token en base de datos
            access_token_lifetime = api_settings.ACCESS_TOKEN_LIFETIME
            expires_at = timezone.now() + access_token_lifetime
            ip_address = self.request.META.get('REMOTE_ADDR')
            user_agent = self.request.META.get('HTTP_USER_AGENT', '')
            
            TokenSession.objects.create(
                usuario=usuario,
                access_token=access_token_str,
                refresh_token=refresh_token_str,
                expires_at=expires_at,
                ip_address=ip_address,
                user_agent=user_agent[:255],
                is_active=True
            )
            
            return Response({
                'usuario': UsuarioSerializer(usuario).data,
                'access': access_token_str,
                'refresh': refresh_token_str,
                'mensaje': 'Usuario registrado exitosamente'
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """
        Obtener tokens JWT con correo y contraseña
        Acepta: correo, password
        Retorna: access token, refresh token y datos del usuario
        """
        correo = request.data.get('correo')
        password = request.data.get('password')
        
        if not correo or not password:
            return Response(
                {'error': 'Se requieren correo y password'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            usuario = Usuario.objects.get(correo=correo)
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Credenciales inválidas'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not usuario.check_password(password):
            return Response(
                {'error': 'Credenciales inválidas'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not usuario.is_active:
            return Response(
                {'error': 'El usuario está desactivado'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Desactivar sesiones previas del usuario (logout de otros dispositivos)
        TokenSession.objects.filter(usuario=usuario, is_active=True).update(is_active=False)
        
        # Generar tokens JWT
        refresh = TokenObtainPairSerializerPersonalizado.get_token(usuario)
        access_token_str = str(refresh.access_token)
        refresh_token_str = str(refresh)
        access_token_lifetime = api_settings.ACCESS_TOKEN_LIFETIME
        expires_at = timezone.now() + access_token_lifetime
        
        # Validar que los tokens no existan para otro usuario
        if TokenSession.objects.filter(access_token=access_token_str, is_active=True).exclude(usuario=usuario).exists():
            return Response(
                {'error': 'Error de generación de token. Intenta login de nuevo.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Obtener IP y User-Agent
        ip_address = self.request.META.get('REMOTE_ADDR')
        user_agent = self.request.META.get('HTTP_USER_AGENT', '')
        
        # Guardar token en base de datos
        TokenSession.objects.create(
            usuario=usuario,
            access_token=access_token_str,
            refresh_token=refresh_token_str,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent[:255],
            is_active=True
        )
        
        return Response({
            'usuario': UsuarioSerializer(usuario).data,
            'access': access_token_str,
            'refresh': refresh_token_str,
            'mensaje': 'Login exitoso'
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def perfil(self, request):
        """
        Obtener el perfil del usuario autenticado
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def cambiar_password(self, request):
        """
        Cambiar la contraseña del usuario autenticado
        Acepta: password_actual, password_nuevo
        """
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
        """
        Logout: marca el token como inactivo en la base de datos
        Acepta: access token en header Authorization
        """
        token = request.auth
        
        try:
            # Obtener el token de la sesión
            token_session = TokenSession.objects.get(
                access_token=str(token),
                usuario=request.user,
                is_active=True
            )
            token_session.is_active = False
            token_session.save()
            
            return Response({
                'mensaje': 'Logout exitoso'
            }, status=status.HTTP_200_OK)
        except TokenSession.DoesNotExist:
            return Response(
                {'error': 'Token no encontrado o ya fue invalidado'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def sesiones_activas(self, request):
        """
        Obtener todas las sesiones activas del usuario autenticado
        """
        sesiones = TokenSession.objects.filter(
            usuario=request.user,
            is_active=True
        ).values(
            'id', 'created_at', 'expires_at', 'ip_address', 'user_agent'
        )
        return Response({
            'sesiones': sesiones,
            'total': sesiones.count()
        }, status=status.HTTP_200_OK)