from rest_framework import serializers
from .models import Player, MatchSet, MatchData, MatchScore, MatchPoint, MatchGame


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['id_player', 'name']
        read_only_fields = ['id_player']


class MatchGameSerializer(serializers.ModelSerializer):
    winner = PlayerSerializer(source='winner_id', read_only=True)
    winner_id_display = serializers.PrimaryKeyRelatedField(
        source='winner_id',
        queryset=Player.objects.all(),
        write_only=True
    )
    
    class Meta:
        model = MatchGame
        fields = ['id_game', 'id_set', 'p1_game_final_score', 'p2_game_final_score', 
                  'duration', 'winner', 'winner_id_display', 'is_break', 'created_at', 'updated_at']
        read_only_fields = ['id_game', 'created_at', 'updated_at']


class MatchPointSerializer(serializers.ModelSerializer):
    player_1 = PlayerSerializer(source='id_player_1', read_only=True)
    player_2 = PlayerSerializer(source='id_player_2', read_only=True)
    winner = PlayerSerializer(source='winner_id', read_only=True)
    
    id_player_1_display = serializers.PrimaryKeyRelatedField(
        source='id_player_1',
        queryset=Player.objects.all(),
        write_only=True
    )
    id_player_2_display = serializers.PrimaryKeyRelatedField(
        source='id_player_2',
        queryset=Player.objects.all(),
        write_only=True
    )
    winner_id_display = serializers.PrimaryKeyRelatedField(
        source='winner_id',
        queryset=Player.objects.all(),
        write_only=True
    )
    
    class Meta:
        model = MatchPoint
        fields = ['id_point', 'id_game', 'player_1', 'player_2', 'winner', 
                  'id_player_1_display', 'id_player_2_display', 'winner_id_display',
                  'score_player_1', 'score_player_2', 'duration', 
                  'break_point_chance', 'break_point', 'created_at']
        read_only_fields = ['id_point', 'created_at']


class MatchSetSerializer(serializers.ModelSerializer):
    winner = PlayerSerializer(source='winner_id', read_only=True)
    winner_id_display = serializers.PrimaryKeyRelatedField(
        source='winner_id',
        queryset=Player.objects.all(),
        write_only=True
    )
    
    class Meta:
        model = MatchSet
        fields = ['id_set', 'id_match_score', 'score_player_1', 'score_player_2', 
                  'winner', 'winner_id_display', 'duration']
        read_only_fields = ['id_set']


class MatchScoreSerializer(serializers.ModelSerializer):
    winner = PlayerSerializer(source='winner_id', read_only=True)
    match_sets = MatchSetSerializer(many=True, read_only=True)
    match_points = MatchPointSerializer(many=True, read_only=True)
    
    winner_id_display = serializers.PrimaryKeyRelatedField(
        source='winner_id',
        queryset=Player.objects.all(),
        write_only=True
    )
    
    class Meta:
        model = MatchScore
        fields = ['id_match_score', 'id_partido', 'winner', 'winner_id_display', 
                  'duration', 'match_sets', 'match_points', 'created_at', 'updated_at']
        read_only_fields = ['id_match_score', 'created_at', 'updated_at']


class MatchDataSerializer(serializers.ModelSerializer):
    player_1 = PlayerSerializer(read_only=True)
    player_2 = PlayerSerializer(read_only=True)
    match_scores = MatchScoreSerializer(many=True, read_only=True)
    
    player_1_id = serializers.PrimaryKeyRelatedField(
        source='player_1',
        queryset=Player.objects.all(),
        write_only=True
    )
    player_2_id = serializers.PrimaryKeyRelatedField(
        source='player_2',
        queryset=Player.objects.all(),
        write_only=True
    )
    
    class Meta:
        model = MatchData
        fields = ['id_match', 'player_1', 'player_2', 'player_1_id', 'player_2_id',
                  'location', 'surface', 'id_match_score', 'match_scores',
                  'created_at', 'updated_at']
        read_only_fields = ['id_match', 'id_match_score', 'created_at', 'updated_at']
