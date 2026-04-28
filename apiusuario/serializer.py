from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Usuario

class UsuarioSerializer(serializers.ModelSerializer):
    UsuarioRol = serializers.CharField(source='get_nivelUsuario_display', read_only=True)
    
    class Meta:
        model = Usuario
        fields = '__all__'
        extra_kwargs = {
            'contraseña': {'write_only': True}
        }
    
    def create(self, validated_data):
        password = validated_data.pop('contraseña', None)
        usuario = Usuario(**validated_data)
        if password:
            # Encriptar la contraseña
            usuario.contraseña = make_password(password)
        usuario.save()
        return usuario
    
    def update(self, instance, validated_data):
        password = validated_data.pop('contraseña', None)
        if password:
            instance.contraseña = make_password(password)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance