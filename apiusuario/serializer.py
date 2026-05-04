from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Usuario

class UsuarioSerializer(serializers.ModelSerializer):
    UsuarioRol = serializers.CharField(source='get_nivelUsuario_display', read_only=True)
    
    class Meta:
        model = Usuario
        fields = ['id', 'nombre', 'apellidoPaterno', 'apellidoMaterno', 'password','correo', 'sexo', 'edad', 'altura', 'peso', 'nivelUsuario', 'UsuarioRol']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        return Usuario.objects.create_user(**validated_data)


class TokenObtainPairSerializerPersonalizado(TokenObtainPairSerializer):
    """
    Serializer personalizado que usa 'correo' en lugar de 'username'
    """
    username_field = 'correo'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['correo'] = self.fields.pop('username')
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Agregar datos personalizados al token
        token['correo'] = user.correo
        token['nombre'] = user.nombre
        return token