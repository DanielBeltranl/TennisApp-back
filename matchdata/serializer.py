from rest_framework_simplejwt import serializers
from matchdata.models import MatchData


class MatchDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchData
        fields = '__all__'