from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import MatchData, MatchScore, MatchSet, MatchPoint, MatchGame

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


class MatchDataSerializer(serializers.ModelSerializer):
    player_1 = UsuarioResumenSerializer(read_only=True)
    player_2 = UsuarioResumenSerializer(read_only=True)
    player_1_id = serializers.PrimaryKeyRelatedField(source='player_1', queryset=Usuario.objects.all(), write_only=True)
    player_2_id = serializers.PrimaryKeyRelatedField(source='player_2', queryset=Usuario.objects.all(), write_only=True)
    score = MatchScoreSerializer(source='match_score', read_only=True)

    class Meta:
        model = MatchData
        fields = [
            'id_match', 'player_1', 'player_2', 'player_1_id', 'player_2_id',
            'location', 'surface', 'best_of', 'match_state',
            'score', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id_match', 'created_at', 'updated_at']
