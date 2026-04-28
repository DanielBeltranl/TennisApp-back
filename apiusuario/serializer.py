from rest_framework import serializers
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