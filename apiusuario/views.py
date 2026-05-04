from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializer import UsuarioSerializer, TokenObtainPairSerializerPersonalizado
from .models import Usuario
from rest_framework import permissions


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
            refresh = RefreshToken.for_user(usuario)
            return Response({
                'usuario': UsuarioSerializer(usuario).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'mensaje': 'Usuario registrado exitosamente'
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        
        # Generar tokens JWT
        refresh = RefreshToken.for_user(usuario)
        
        return Response({
            'usuario': UsuarioSerializer(usuario).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'mensaje': 'Login exitoso'
        }, status=status.HTTP_200_OK)
