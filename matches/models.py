import uuid

from django.db import models

# Create your models here.

class Player(models.Model):
    id_player = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'player'

    def __str__(self):
        return self.name

class MatchData(models.Model):
    id_match = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    player_1 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player_1_matches')
    player_2 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player_2_matches')
    location = models.CharField(max_length=100)
    surface = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'match_data'
        unique_together = ('player_1', 'player_2')

    def __str__(self):
        return f"{self.player_1} vs {self.player_2} at {self.location}"


class MatchScore(models.Model):
    id_match_score = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_partido = models.ForeignKey(MatchData, on_delete=models.CASCADE, related_name='match_scores')
    winner_id = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='match_wins')
    duration = models.DurationField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'match_score'
        unique_together = ('id_partido', 'winner_id')

    def __str__(self):
        return f"Score for {self.id_partido}: {self.winner_id}"

    
class MatchSet(models.Model):
    id_set = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_match_score = models.ForeignKey(MatchScore, on_delete=models.CASCADE, related_name='match_sets') 
    score_player_1 = models.IntegerField()
    score_player_2 = models.IntegerField()
    winner_id = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='set_wins')
    duration = models.DurationField()

    class Meta:
        db_table = 'match_set'

    def __str__(self):
        return f"Set in match {self.id_match_score} with score {self.score_player_1}-{self.score_player_2}"
    
class MatchGame(models.Model):
    id_game = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_set = models.ForeignKey(MatchSet, on_delete=models.CASCADE, related_name='match_games')
    p1_game_final_score = models.IntegerField()
    p2_game_final_score = models.IntegerField()
    duration = models.DurationField()
    winner_id = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='game_wins')
    is_break = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'match_game'
        unique_together = ('id_set', 'winner_id')

    def __str__(self):
        return f"Game in set {self.id_set} with score {self.p1_game_final_score}-{self.p2_game_final_score}"
    
class MatchPoint(models.Model):
    id_point = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_game = models.ForeignKey(MatchScore, on_delete=models.CASCADE, related_name='match_points')
    id_player_1 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player_1_points')
    id_player_2 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player_2_points')
    winner_id = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='point_wins')
    score_player_1 = models.IntegerField()
    score_player_2 = models.IntegerField()
    duration = models.DurationField()
    break_point_chance = models.BooleanField()
    break_point = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'match_point'
        unique_together = ('id_game', 'id_player_1', 'id_player_2', 'winner_id')

    def __str__(self):
        return f"Point in game {self.id_game} between {self.id_player_1} and {self.id_player_2}"