from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import MatchData, MatchScore, MatchSet, MatchPoint, MatchGame, MatchState

Usuario = get_user_model()


class UsuarioResumenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'nombre', 'apellidoPaterno', 'correo']
        read_only_fields = fields


class MatchGameSerializer(serializers.ModelSerializer):
    winner = UsuarioResumenSerializer(source='winner_id', read_only=True)
    winner_id = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all(), write_only=True)
    is_serving = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all())

    class Meta:
        model = MatchGame
        fields = [
            'id_game', 'id_set', 'p1_game_final_score', 'p2_game_final_score',
            'duration', 'winner', 'winner_id', 'is_break', 'is_serving',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id_game', 'created_at', 'updated_at']


class MatchPointSerializer(serializers.ModelSerializer):
    player_1 = UsuarioResumenSerializer(source='id_player_1', read_only=True)
    player_2 = UsuarioResumenSerializer(source='id_player_2', read_only=True)
    winner = UsuarioResumenSerializer(source='winner_id', read_only=True)
    id_player_1 = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all(), write_only=True)
    id_player_2 = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all(), write_only=True)
    winner_id = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all(), write_only=True)
    is_serving = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all())

    class Meta:
        model = MatchPoint
        fields = [
            'id_point', 'id_game', 'is_serving',
            'player_1', 'player_2', 'winner',
            'id_player_1', 'id_player_2', 'winner_id',
            'score_p1', 'score_p2', 'duration',
            'break_point_chance', 'break_point', 'created_at',
        ]
        read_only_fields = ['id_point', 'created_at']


class MatchSetSerializer(serializers.ModelSerializer):
    winner = UsuarioResumenSerializer(source='winner_id', read_only=True)
    winner_id = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all(), write_only=True)
    games = MatchGameSerializer(source='match_games', many=True, read_only=True)

    class Meta:
        model = MatchSet
        fields = [
            'id_set', 'id_match_score', 'score_p1', 'score_p2',
            'winner', 'winner_id', 'duration', 'created_at', 'games',
        ]
        read_only_fields = ['id_set', 'created_at']


class MatchScoreSerializer(serializers.ModelSerializer):
    winner = UsuarioResumenSerializer(source='winner_id', read_only=True)
    winner_id = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all(), write_only=True)
    sets = MatchSetSerializer(source='match_sets', many=True, read_only=True)

    class Meta:
        model = MatchScore
        fields = [
            'id_match_score', 'id_partido', 'winner', 'winner_id',
            'duration', 'sets', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id_match_score', 'created_at', 'updated_at']


class ScheduleMatchSerializer(serializers.ModelSerializer):
    id_local_player = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(), write_only=True,
    )
    id_invited_player = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(), required=False, allow_null=True,
    )
    scheduled_at = serializers.DateTimeField(required=True)
    guest_name = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True)
    local_player = UsuarioResumenSerializer(source='id_local_player', read_only=True)
    invited = UsuarioResumenSerializer(source='id_invited_player', read_only=True)
    entrenador = UsuarioResumenSerializer(source='id_entrenador', read_only=True)

    class Meta:
        model = MatchData
        fields = [
            'id_match', 'entrenador', 'local_player', 'invited',
            'id_local_player', 'id_invited_player',
            'scheduled_at', 'guest_name', 'location', 'surface', 'best_of',
            'match_state', 'created_at',
        ]
        read_only_fields = ['id_match', 'match_state', 'created_at']

    def validate(self, data):
        invited = data.get('id_invited_player')
        guest_name = data.get('guest_name', '').strip() if data.get('guest_name') else ''
        coach = self.context['request'].user
        local_player = data.get('id_local_player')

        if invited and guest_name:
            raise serializers.ValidationError('Enviá id_invited_player o guest_name, no ambos.')
        if not invited and not guest_name:
            raise serializers.ValidationError('Debés enviar id_invited_player o guest_name.')

        if local_player and getattr(local_player, 'entrenador', None) != coach:
            raise serializers.ValidationError({'id_local_player': 'El jugador local debe ser uno de tus entrenados.'})

        return data

    def create(self, validated_data):
        validated_data['id_entrenador'] = self.context['request'].user
        is_guest = not validated_data.get('id_invited_player')
        validated_data['match_state'] = MatchState.ACEPTADO if is_guest else MatchState.PENDIENTE
        return super().create(validated_data)


class MatchDataSerializer(serializers.ModelSerializer):
    local_player = UsuarioResumenSerializer(source='id_local_player', read_only=True)
    invited = UsuarioResumenSerializer(source='id_invited_player', read_only=True)
    entrenador = UsuarioResumenSerializer(source='id_entrenador', read_only=True)
    id_local_player = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all(), write_only=True)
    id_invited_player = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(), write_only=True, required=False, allow_null=True,
    )
    score = MatchScoreSerializer(source='match_score', read_only=True)

    class Meta:
        model = MatchData
        fields = [
            'id_match', 'entrenador', 'local_player', 'invited',
            'id_local_player', 'id_invited_player',
            'guest_name', 'location', 'surface', 'best_of', 'match_state',
            'scheduled_at', 'score', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id_match', 'created_at', 'updated_at']


class GameSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchGame
        fields = ['p1_game_final_score', 'p2_game_final_score']


class SetSummarySerializer(serializers.ModelSerializer):
    games = GameSummarySerializer(source='match_games', many=True, read_only=True)

    class Meta:
        model = MatchSet
        fields = ['score_p1', 'score_p2', 'games']


class MatchSummarySerializer(serializers.ModelSerializer):
    local_player = UsuarioResumenSerializer(source='id_local_player', read_only=True)
    invited = UsuarioResumenSerializer(source='id_invited_player', read_only=True)
    entrenador = UsuarioResumenSerializer(source='id_entrenador', read_only=True)
    winner = UsuarioResumenSerializer(source='match_score.winner_id', read_only=True)
    duration = serializers.IntegerField(source='match_score.duration', read_only=True)
    sets = SetSummarySerializer(source='match_score.match_sets', many=True, read_only=True)

    class Meta:
        model = MatchData
        fields = [
            'id_match', 'entrenador', 'local_player', 'invited', 'guest_name',
            'location', 'surface', 'best_of', 'match_state',
            'winner', 'duration', 'sets', 'scheduled_at', 'created_at',
        ]
