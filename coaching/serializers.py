from rest_framework import serializers
from django.contrib.auth import get_user_model
from apiusuario.models import NivelUsuario, RolUsuario
from .models import SolicitudAsociacion, EstadoSolicitud

Usuario = get_user_model()


class EntrenadorResumenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'nombre', 'apellidoPaterno', 'apellidoMaterno', 'correo']
        read_only_fields = fields


class JugadorResumenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'nombre', 'apellidoPaterno', 'apellidoMaterno', 'correo', 'nivelUsuario']
        read_only_fields = fields


class JugadorBusquedaSerializer(serializers.ModelSerializer):
    entrenador_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = ['id', 'nombre', 'apellidoPaterno', 'entrenador_nombre']
        read_only_fields = fields

    def get_entrenador_nombre(self, obj):
        if obj.entrenador:
            return f"{obj.entrenador.nombre} {obj.entrenador.apellidoPaterno}"
        return None


class SolicitudAsociacionSerializer(serializers.ModelSerializer):
    jugador = EntrenadorResumenSerializer(read_only=True)
    entrenador = EntrenadorResumenSerializer(read_only=True)

    class Meta:
        model = SolicitudAsociacion
        fields = ['id', 'jugador', 'entrenador', 'status', 'created_at', 'updated_at']
        read_only_fields = fields


class EnviarSolicitudSerializer(serializers.Serializer):
    entrenador_id = serializers.IntegerField()

    def validate_entrenador_id(self, value):
        try:
            entrenador = Usuario.objects.get(id=value, rol=RolUsuario.entrenador, is_active=True)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError('Entrenador no encontrado.')
        self.context['entrenador'] = entrenador
        return value

    def validate(self, data):
        jugador = self.context['request'].user

        if jugador.entrenador_id:
            raise serializers.ValidationError('Ya tenés un entrenador asignado.')

        entrenador = self.context['entrenador']
        if SolicitudAsociacion.objects.filter(
            jugador=jugador,
            entrenador=entrenador,
            status=EstadoSolicitud.pendiente,
        ).exists():
            raise serializers.ValidationError('Ya tenés una solicitud pendiente con este entrenador.')

        return data

    def create(self, validated_data):
        return SolicitudAsociacion.objects.create(
            jugador=self.context['request'].user,
            entrenador=self.context['entrenador'],
        )


class AceptarSolicitudSerializer(serializers.Serializer):
    nivel = serializers.ChoiceField(choices=NivelUsuario.choices)
