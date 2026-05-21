from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Friendship

Usuario = get_user_model()


class PlayerSearchSerializer(serializers.Serializer):
    player_id = serializers.IntegerField()
    correo = serializers.EmailField()
    display_name = serializers.CharField()
    nivel = serializers.CharField()
    button_state = serializers.CharField()


class SendFriendRequestSerializer(serializers.Serializer):
    friend_id = serializers.IntegerField()

    def validate_friend_id(self, value):
        request = self.context['request']

        if value == request.user.id:
            raise serializers.ValidationError('No puedes enviarte una solicitud a ti mismo.')

        if not Usuario.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError('Usuario no encontrado.')

        if Friendship.objects.filter(user=request.user, friend_id=value).exists():
            raise serializers.ValidationError('Ya existe una relación con este usuario.')

        if Friendship.objects.filter(user_id=value, friend=request.user).exists():
            raise serializers.ValidationError('Este usuario ya te envió una solicitud.')

        return value


class UserResumenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'nombre', 'apellidoPaterno', 'correo', 'nivelUsuario']


class FriendshipSerializer(serializers.ModelSerializer):
    user = UserResumenSerializer(read_only=True)
    friend = UserResumenSerializer(read_only=True)

    class Meta:
        model = Friendship
        fields = ['id', 'user', 'friend', 'status', 'created_at']
