from django.contrib import admin
from .models import MatchData, MatchScore, MatchSet, MatchGame, MatchPoint

admin.site.register(MatchData)
admin.site.register(MatchScore)
admin.site.register(MatchSet)
admin.site.register(MatchGame)
admin.site.register(MatchPoint)

