from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import MatchData, MatchScore, MatchSet, MatchPoint, MatchGame, MatchState
from .serializer import (
    MatchDataSerializer,
    MatchScoreSerializer,
    MatchSetSerializer,
    MatchPointSerializer,
    MatchGameSerializer,
    ScheduleMatchSerializer,
    UsuarioResumenSerializer,
)

Usuario = get_user_model()


class ScheduleMatchView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ScheduleMatchSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        match = serializer.save()
        return Response(ScheduleMatchSerializer(match, context={'request': request}).data, status=status.HTTP_201_CREATED)


class AcceptMatchView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            match = MatchData.objects.get(id_match=pk)
        except MatchData.DoesNotExist:
            return Response({'error': 'Partido no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        if match.id_player_invited_id != request.user.id:
            return Response({'error': 'Solo el jugador invitado puede aceptar.'}, status=status.HTTP_403_FORBIDDEN)

        if match.match_state != MatchState.PENDIENTE:
            return Response({'error': f'El partido no está en estado PENDIENTE (estado actual: {match.match_state}).'}, status=status.HTTP_400_BAD_REQUEST)

        match.match_state = MatchState.ACEPTADO
        match.save()
        return Response(MatchDataSerializer(match).data)


class RejectMatchView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            match = MatchData.objects.get(id_match=pk)
        except MatchData.DoesNotExist:
            return Response({'error': 'Partido no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        if match.id_player_invited_id != request.user.id:
            return Response({'error': 'Solo el jugador invitado puede rechazar.'}, status=status.HTTP_403_FORBIDDEN)

        if match.match_state != MatchState.PENDIENTE:
            return Response({'error': f'Solo se puede rechazar un partido PENDIENTE (estado actual: {match.match_state}).'}, status=status.HTTP_400_BAD_REQUEST)

        match.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StartMatchView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            match = MatchData.objects.get(id_match=pk)
        except MatchData.DoesNotExist:
            return Response({'error': 'Partido no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        participant_ids = {match.id_player_creator_id, match.id_player_invited_id}
        if request.user.id not in participant_ids:
            return Response({'error': 'No sos participante de este partido.'}, status=status.HTTP_403_FORBIDDEN)

        if match.match_state != MatchState.ACEPTADO:
            return Response({'error': f'El partido no está en estado ACEPTADO (estado actual: {match.match_state}).'}, status=status.HTTP_400_BAD_REQUEST)

        first_server_id = request.data.get('first_server_id')
        if not first_server_id:
            return Response({'error': 'first_server_id es requerido.'}, status=status.HTTP_400_BAD_REQUEST)

        if int(first_server_id) not in participant_ids:
            return Response({'error': 'El servidor inicial debe ser participante del partido.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            first_server = Usuario.objects.get(id=first_server_id)
        except Usuario.DoesNotExist:
            return Response({'error': 'Jugador no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            match_score = MatchScore.objects.create(id_partido=match)
            first_set = MatchSet.objects.create(id_match_score=match_score)
            MatchGame.objects.create(id_set=first_set, is_serving=first_server)
            match.id_match_score = match_score
            match.match_state = MatchState.INICIADO
            match.save()

        return Response(MatchDataSerializer(match).data)


class PauseMatchView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            match = MatchData.objects.get(id_match=pk)
        except MatchData.DoesNotExist:
            return Response({'error': 'Partido no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        if request.user.id not in {match.id_player_creator_id, match.id_player_invited_id}:
            return Response({'error': 'No sos participante de este partido.'}, status=status.HTTP_403_FORBIDDEN)

        if match.match_state != MatchState.INICIADO:
            return Response({'error': f'El partido no está en estado INICIADO (estado actual: {match.match_state}).'}, status=status.HTTP_400_BAD_REQUEST)

        match.match_state = MatchState.PAUSADO
        match.save()
        return Response(MatchDataSerializer(match).data)


class ResumeMatchView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            match = MatchData.objects.get(id_match=pk)
        except MatchData.DoesNotExist:
            return Response({'error': 'Partido no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        if request.user.id not in {match.id_player_creator_id, match.id_player_invited_id}:
            return Response({'error': 'No sos participante de este partido.'}, status=status.HTTP_403_FORBIDDEN)

        if match.match_state != MatchState.PAUSADO:
            return Response({'error': f'El partido no está en estado PAUSADO (estado actual: {match.match_state}).'}, status=status.HTTP_400_BAD_REQUEST)

        match.match_state = MatchState.INICIADO
        match.save()
        return Response(MatchDataSerializer(match).data)


class FinishMatchView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            match = MatchData.objects.get(id_match=pk)
        except MatchData.DoesNotExist:
            return Response({'error': 'Partido no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        participant_ids = {match.id_player_creator_id, match.id_player_invited_id}
        if request.user.id not in participant_ids:
            return Response({'error': 'No sos participante de este partido.'}, status=status.HTTP_403_FORBIDDEN)

        if match.match_state != MatchState.INICIADO:
            return Response({'error': f'El partido no está en estado INICIADO (estado actual: {match.match_state}).'}, status=status.HTTP_400_BAD_REQUEST)

        winner_id = request.data.get('winner_id')
        if not winner_id:
            return Response({'error': 'winner_id es requerido.'}, status=status.HTTP_400_BAD_REQUEST)

        if int(winner_id) not in participant_ids:
            return Response({'error': 'El ganador debe ser participante del partido.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            winner = Usuario.objects.get(id=winner_id)
        except Usuario.DoesNotExist:
            return Response({'error': 'Jugador no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            match_score = match.match_score
        except MatchScore.DoesNotExist:
            return Response({'error': 'El partido no tiene marcador iniciado.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            match_score.winner_id = winner
            match_score.duration = int((timezone.now() - match_score.created_at).total_seconds())
            match_score.save()
            match.match_state = MatchState.FINALIZADA
            match.save()

        return Response(MatchDataSerializer(match).data)


class RecoverMatchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            match = MatchData.objects.select_related(
                'id_player_creator', 'id_player_invited'
            ).get(id_match=pk)
        except MatchData.DoesNotExist:
            return Response({'error': 'Partido no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        if request.user.id not in {match.id_player_creator_id, match.id_player_invited_id}:
            return Response({'error': 'No sos participante de este partido.'}, status=status.HTTP_403_FORBIDDEN)

        if match.match_state not in {MatchState.INICIADO, MatchState.PAUSADO}:
            return Response({'error': 'El partido no está en curso.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            match_score = match.match_score
        except MatchScore.DoesNotExist:
            return Response({'error': 'El partido no tiene marcador iniciado.'}, status=status.HTTP_400_BAD_REQUEST)

        all_sets = list(
            MatchSet.objects.filter(id_match_score=match_score)
            .select_related('winner_id')
            .order_by('created_at')
        )

        sets_p1 = sum(1 for s in all_sets if s.winner_id_id == match.id_player_creator_id)
        sets_p2 = sum(1 for s in all_sets if s.winner_id_id == match.id_player_invited_id)

        completed_sets = [
            {
                'id_set': s.id_set,
                'set_number': i + 1,
                'score_p1': s.score_p1,
                'score_p2': s.score_p2,
                'winner_id': s.winner_id_id,
            }
            for i, s in enumerate(all_sets)
        ]

        current_set = next((s for s in reversed(all_sets) if s.winner_id_id is None), None)

        current_game_data = None
        current_score = {'score_p1': '0', 'score_p2': '0'}
        last_point = None

        if current_set:
            games = list(
                MatchGame.objects.filter(id_set=current_set)
                .select_related('winner_id', 'is_serving')
                .order_by('created_at')
            )
            current_game_obj = next((g for g in reversed(games) if g.winner_id_id is None), None)

            if current_game_obj:
                last_point_obj = (
                    MatchPoint.objects.filter(id_game=current_game_obj)
                    .select_related('winner_id', 'is_serving')
                    .order_by('-created_at')
                    .first()
                )

                current_game_data = {
                    'id_game': current_game_obj.id_game,
                    'game_number': len(games),
                    'is_serving': UsuarioResumenSerializer(current_game_obj.is_serving).data,
                }

                if last_point_obj:
                    current_score = {
                        'score_p1': last_point_obj.score_p1,
                        'score_p2': last_point_obj.score_p2,
                    }
                    last_point = {
                        'id_point': last_point_obj.id_point,
                        'score_p1': last_point_obj.score_p1,
                        'score_p2': last_point_obj.score_p2,
                        'winner_id': last_point_obj.winner_id_id,
                        'duration': last_point_obj.duration,
                        'created_at': last_point_obj.created_at,
                    }

        return Response({
            'match': MatchDataSerializer(match).data,
            'sets_p1': sets_p1,
            'sets_p2': sets_p2,
            'sets': completed_sets,
            'current_set': {
                'id_set': current_set.id_set,
                'set_number': len(all_sets),
                'score_p1': current_set.score_p1,
                'score_p2': current_set.score_p2,
            } if current_set else None,
            'current_game': current_game_data,
            'current_score': current_score,
            'last_point': last_point,
        })


class MyCreatedMatchesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        matches = MatchData.objects.filter(
            id_player_creator=request.user
        ).select_related('id_player_creator', 'id_player_invited').order_by('-created_at')
        return Response(MatchDataSerializer(matches, many=True).data)


class MyInvitedMatchesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        matches = MatchData.objects.filter(
            id_player_invited=request.user
        ).select_related('id_player_creator', 'id_player_invited').order_by('-created_at')
        return Response(MatchDataSerializer(matches, many=True).data)


class MatchDataViewSet(viewsets.ModelViewSet):
    queryset = MatchData.objects.all().select_related('id_player_creator', 'id_player_invited')
    serializer_class = MatchDataSerializer
    permission_classes = [IsAuthenticated]


class MatchScoreViewSet(viewsets.ModelViewSet):
    queryset = MatchScore.objects.all().select_related('winner_id', 'id_partido')
    serializer_class = MatchScoreSerializer
    permission_classes = [IsAuthenticated]


class MatchSetViewSet(viewsets.ModelViewSet):
    queryset = MatchSet.objects.all().select_related('winner_id', 'id_match_score')
    serializer_class = MatchSetSerializer
    permission_classes = [IsAuthenticated]


class MatchPointViewSet(viewsets.ModelViewSet):
    queryset = MatchPoint.objects.all().select_related('id_player_1', 'id_player_2', 'winner_id', 'id_game')
    serializer_class = MatchPointSerializer
    permission_classes = [IsAuthenticated]


class MatchGameViewSet(viewsets.ModelViewSet):
    queryset = MatchGame.objects.all().select_related('winner_id', 'id_set')
    serializer_class = MatchGameSerializer
    permission_classes = [IsAuthenticated]
