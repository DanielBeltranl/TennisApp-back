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
        password=validated_data.pop('password',None)
        instance = self.Meta.model(**validated_data)
        
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class TokenObtainPairSerializerPersonalizado(TokenObtainPairSerializer):
    """
    Serializer personalizado que usa 'correo' en lugar de 'username'
    """
    username_field = 'correo'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo hacer pop si el field 'username' existe
        if 'username' in self.fields:
            self.fields['correo'] = self.fields.pop('username')
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['correo'] = user.correo
        token['nombre'] = user.nombre
        token['nivelUsuario'] = user.nivelUsuario
        token['sexo'] = user.sexo
        return token