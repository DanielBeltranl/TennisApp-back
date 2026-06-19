from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Usuario, RolUsuario


class UsuarioPerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            'id', 'nombre', 'apellidoPaterno', 'apellidoMaterno',
            'correo', 'rol', 'sexo', 'fecha_nacimiento',
            'altura', 'peso', 'nivelUsuario',
        ]
        read_only_fields = fields


class JugadorRegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = [
            'nombre', 'apellidoPaterno', 'apellidoMaterno',
            'correo', 'password', 'rol',
            'sexo', 'fecha_nacimiento', 'altura', 'peso',
        ]

    def validate(self, data):
        for campo in ('sexo', 'fecha_nacimiento', 'altura', 'peso'):
            if not data.get(campo):
                raise serializers.ValidationError({campo: 'Este campo es obligatorio para jugadores.'})
        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        usuario = Usuario(**validated_data)
        usuario.set_password(password)
        usuario.save()
        return usuario


class EntrenadorRegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    # The model field is null/blank, so ModelSerializer would infer required=False
    # and DRF would skip the field validator when the key is absent. Declaring it
    # explicitly forces the field to be present for coach registration.
    fecha_nacimiento = serializers.DateField(required=True)

    class Meta:
        model = Usuario
        fields = [
            'nombre', 'apellidoPaterno', 'apellidoMaterno',
            'correo', 'password', 'rol', 'fecha_nacimiento',
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        usuario = Usuario(**validated_data)
        usuario.set_password(password)
        usuario.save()
        return usuario


class TokenObtainPairSerializerPersonalizado(TokenObtainPairSerializer):
    username_field = 'correo'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'username' in self.fields:
            self.fields['correo'] = self.fields.pop('username')

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['correo'] = user.correo
        token['nombre'] = user.nombre
        token['rol'] = user.rol
        token['nivelUsuario'] = user.nivelUsuario
        token['sexo'] = user.sexo
        return token
