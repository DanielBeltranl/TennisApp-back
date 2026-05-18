import uuid
from django.conf import settings
from django.db import models


class BestOf(models.IntegerChoices):
    ONE = 1
    THREE = 3
    FIVE = 5


class MatchState(models.TextChoices):
    INICIADO = 'INICIADO'
    PAUSADO = 'PAUSADO'
    FINALIZADA = 'FINALIZADA'


class MatchData(models.Model):
    id_match = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    player_1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='player_1_matches')
    player_2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='player_2_matches')
    location = models.CharField(max_length=100)
    surface = models.CharField(max_length=50)
    best_of = models.IntegerField(choices=BestOf.choices)
    match_state = models.CharField(max_length=20, choices=MatchState.choices, default=MatchState.INICIADO)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'match_data'

    def __str__(self):
        return f"{self.player_1} vs {self.player_2} at {self.location}"


class MatchScore(models.Model):
    id_match_score = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_partido = models.OneToOneField(MatchData, on_delete=models.CASCADE, related_name='match_score')
    winner_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='match_wins')
    duration = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'match_score'

    def __str__(self):
        return f"Score for {self.id_partido}: {self.winner_id}"


class MatchSet(models.Model):
    id_set = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_match_score = models.ForeignKey(MatchScore, on_delete=models.CASCADE, related_name='match_sets')
    score_p1 = models.IntegerField()
    score_p2 = models.IntegerField()
    winner_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='set_wins')
    duration = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'match_set'

    def __str__(self):
        return f"Set in match {self.id_match_score} with score {self.score_p1}-{self.score_p2}"


class MatchGame(models.Model):
    id_game = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_set = models.ForeignKey(MatchSet, on_delete=models.CASCADE, related_name='match_games')
    p1_game_final_score = models.IntegerField()
    p2_game_final_score = models.IntegerField()
    duration = models.IntegerField()
    winner_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='game_wins')
    is_break = models.BooleanField()
    is_serving = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='games_serving')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'match_game'

    def __str__(self):
        return f"Game in set {self.id_set} with score {self.p1_game_final_score}-{self.p2_game_final_score}"


class MatchPoint(models.Model):
    id_point = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_serving = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='points_serving')
    id_game = models.ForeignKey(MatchGame, on_delete=models.CASCADE, related_name='match_points')
    id_player_1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='player_1_points')
    id_player_2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='player_2_points')
    winner_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='point_wins')
    score_p1 = models.CharField(max_length=5)
    score_p2 = models.CharField(max_length=5)
    duration = models.IntegerField()
    break_point_chance = models.BooleanField()
    break_point = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'match_point'

    def __str__(self):
        return f"Point in game {self.id_game} between {self.id_player_1} and {self.id_player_2}"
