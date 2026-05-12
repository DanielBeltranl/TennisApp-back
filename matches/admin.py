from django.contrib import admin
from .models import Player, MatchSet, MatchData, MatchScore, MatchPoint

# Register your models here.

admin.site.register(Player)
admin.site.register(MatchSet)
admin.site.register(MatchData)
admin.site.register(MatchScore)
admin.site.register(MatchPoint)

