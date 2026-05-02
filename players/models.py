from django.db import models

# Create your models here.

class Player(models.Model):
    player_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.player_id
