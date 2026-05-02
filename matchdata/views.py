from django.shortcuts import render 
from rest_framework.views import APIView, Response
from matchdata.models import MatchData
from matchdata.serializer import MatchDataSerializer
from rest_framework import status
# Create your views here.

class MatchDataView(APIView):
    def get(self, request):
        match_data = MatchData.objects.all()
        serializer = MatchDataSerializer(match_data, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = MatchDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    