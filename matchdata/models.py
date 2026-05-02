from django.db import models

# Create your models here.

class MatchData(models.Model):
    match_id = models.CharField(max_length=255, unique=True)
    id_player_1 = models.ForeignKey('players.Player', on_delete=models.CASCADE, related_name='matches_as_player_1') 
    id_player_2 = models.ForeignKey('players.Player', on_delete=models.CASCADE, related_name='matches_as_player_2') 
    location = models.CharField(max_length=255)
    surface = models.CharField(max_length=255)
    id_matcha_score = models.CharField(max_length=255) #Se espera Foreign Key a un modelo de MatchScore, pero se mantiene como CharField para simplificar
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    data = models.JSONField()

    def __str__(self):
        return self.match_id