from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import MatchData, MatchScore, MatchSet, MatchPoint, MatchGame, MatchState
from .services import (
    advance_score,
    advance_tiebreak_score,
    is_break_point_chance,
    is_break_point,
    is_set_over,
    is_match_over,
    get_next_server,
    get_tiebreak_server,
)
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


class RegisterPointView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            match = MatchData.objects.select_related(
                'id_player_creator', 'id_player_invited'
            ).get(id_match=pk)
        except MatchData.DoesNotExist:
            return Response({'error': 'Partido no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        if request.user.id not in {match.id_player_creator_id, match.id_player_invited_id}:
            return Response({'error': 'No sos participante de este partido.'}, status=status.HTTP_403_FORBIDDEN)

        if match.match_state != MatchState.INICIADO:
            return Response({'error': 'El partido no está en curso.'}, status=status.HTTP_400_BAD_REQUEST)

        winner_id = request.data.get('winner_id')
        duration = request.data.get('duration')

        if not winner_id or duration is None:
            return Response({'error': 'winner_id y duration son requeridos.'}, status=status.HTTP_400_BAD_REQUEST)

        if int(winner_id) not in {match.id_player_creator_id, match.id_player_invited_id}:
            return Response({'error': 'El ganador debe ser participante del partido.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            winner = Usuario.objects.get(id=winner_id)
        except Usuario.DoesNotExist:
            return Response({'error': 'Jugador no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            match_score = match.match_score
        except MatchScore.DoesNotExist:
            return Response({'error': 'El partido no tiene marcador iniciado.'}, status=status.HTTP_400_BAD_REQUEST)

        current_set = MatchSet.objects.filter(
            id_match_score=match_score, winner_id__isnull=True
        ).order_by('created_at').last()

        if not current_set:
            return Response({'error': 'No hay set activo.'}, status=status.HTTP_400_BAD_REQUEST)

        current_game = MatchGame.objects.filter(
            id_set=current_set, winner_id__isnull=True
        ).order_by('created_at').last()

        if not current_game:
            return Response({'error': 'No hay game activo.'}, status=status.HTTP_400_BAD_REQUEST)

        last_point = MatchPoint.objects.filter(
            id_game=current_game
        ).order_by('-created_at').first()

        score_p1 = last_point.score_p1 if last_point else '0'
        score_p2 = last_point.score_p2 if last_point else '0'

        winner_is_creator = (winner.id == match.id_player_creator_id)

        if current_game.is_tiebreak:
            if winner_is_creator:
                new_p1, new_p2, game_over = advance_tiebreak_score(score_p1, score_p2)
            else:
                new_p2, new_p1, game_over = advance_tiebreak_score(score_p2, score_p1)

            point_index = MatchPoint.objects.filter(id_game=current_game).count()
            other_player_id = (
                match.id_player_invited_id
                if current_game.is_serving_id == match.id_player_creator_id
                else match.id_player_creator_id
            )
            tb_server_id = get_tiebreak_server(current_game.is_serving_id, other_player_id, point_index)
            point_server = Usuario.objects.get(id=tb_server_id)
            bp_chance = False
            bp = False
        else:
            if winner_is_creator:
                new_p1, new_p2, game_over = advance_score(score_p1, score_p2)
            else:
                new_p2, new_p1, game_over = advance_score(score_p2, score_p1)

            server_is_creator = (current_game.is_serving_id == match.id_player_creator_id)
            score_server   = score_p1 if server_is_creator else score_p2
            score_receiver = score_p2 if server_is_creator else score_p1
            receiver_won   = (winner_is_creator != server_is_creator)

            bp_chance    = is_break_point_chance(score_server, score_receiver)
            bp           = is_break_point(score_server, score_receiver, receiver_won)
            point_server = current_game.is_serving

        response_data = {
            'game_closed': False,
            'set_closed': False,
            'match_closed': False,
            'tiebreak_required': False,
        }

        with transaction.atomic():
            point = MatchPoint.objects.create(
                id_game=current_game,
                is_serving=point_server,
                id_player_1=match.id_player_creator,
                id_player_2=match.id_player_invited,
                winner_id=winner,
                score_p1=new_p1,
                score_p2=new_p2,
                duration=int(duration),
                break_point_chance=bp_chance,
                break_point=bp,
            )

            response_data['point'] = MatchPointSerializer(point).data
            response_data['current_score'] = {'score_p1': new_p1, 'score_p2': new_p2}

            if not game_over:
                response_data['current_game'] = {'id_game': current_game.id_game, 'is_serving_id': current_game.is_serving_id}
                response_data['current_set']  = {'score_p1': current_set.score_p1, 'score_p2': current_set.score_p2}
                return Response(response_data, status=status.HTTP_201_CREATED)

            # — cerrar game —
            response_data['game_closed'] = True

            if winner_is_creator:
                current_set.score_p1 += 1
            else:
                current_set.score_p2 += 1

            current_game.winner_id         = winner
            current_game.duration          = int((timezone.now() - current_game.created_at).total_seconds())
            current_game.p1_game_final_score = current_set.score_p1
            current_game.p2_game_final_score = current_set.score_p2
            current_game.is_break          = (current_game.is_serving_id != winner.id)
            current_game.save()

            set_over, p1_wins_set, tiebreak = is_set_over(current_set.score_p1, current_set.score_p2)

            if tiebreak:
                current_set.save()
                next_srv_id = get_next_server(current_game.is_serving_id, match.id_player_creator_id, match.id_player_invited_id)
                next_srv    = Usuario.objects.get(id=next_srv_id)
                tb_game     = MatchGame.objects.create(id_set=current_set, is_serving=next_srv, is_tiebreak=True)
                response_data['tiebreak_required'] = True
                response_data['current_set']  = {'score_p1': current_set.score_p1, 'score_p2': current_set.score_p2}
                response_data['current_game'] = {'id_game': tb_game.id_game, 'is_serving_id': next_srv_id, 'is_tiebreak': True}
                return Response(response_data, status=status.HTTP_201_CREATED)

            if not set_over:
                current_set.save()
                next_srv_id = get_next_server(current_game.is_serving_id, match.id_player_creator_id, match.id_player_invited_id)
                next_srv    = Usuario.objects.get(id=next_srv_id)
                new_game    = MatchGame.objects.create(id_set=current_set, is_serving=next_srv)
                response_data['current_set']  = {'score_p1': current_set.score_p1, 'score_p2': current_set.score_p2}
                response_data['current_game'] = {'id_game': new_game.id_game, 'is_serving_id': next_srv_id}
                return Response(response_data, status=status.HTTP_201_CREATED)

            # — cerrar set —
            response_data['set_closed'] = True
            set_winner = match.id_player_creator if p1_wins_set else match.id_player_invited

            current_set.winner_id = set_winner
            current_set.duration  = int((timezone.now() - current_set.created_at).total_seconds())
            current_set.save()

            sets_p1 = MatchSet.objects.filter(id_match_score=match_score, winner_id=match.id_player_creator).count()
            sets_p2 = MatchSet.objects.filter(id_match_score=match_score, winner_id=match.id_player_invited).count()

            match_over, p1_wins_match = is_match_over(sets_p1, sets_p2, match.best_of)

            if not match_over:
                next_srv_id = get_next_server(current_game.is_serving_id, match.id_player_creator_id, match.id_player_invited_id)
                next_srv    = Usuario.objects.get(id=next_srv_id)
                new_set     = MatchSet.objects.create(id_match_score=match_score)
                new_game    = MatchGame.objects.create(id_set=new_set, is_serving=next_srv)
                response_data['current_set']  = {'set_number': sets_p1 + sets_p2 + 1, 'score_p1': 0, 'score_p2': 0}
                response_data['current_game'] = {'id_game': new_game.id_game, 'is_serving_id': next_srv_id}
                return Response(response_data, status=status.HTTP_201_CREATED)

            # — marcar cierre pendiente, sin finalizar en BD —
            response_data['match_closed'] = True
            match_winner = match.id_player_creator if p1_wins_match else match.id_player_invited
            response_data['winner'] = UsuarioResumenSerializer(match_winner).data
            return Response(response_data, status=status.HTTP_201_CREATED)


class UndoPointView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            match = MatchData.objects.select_related(
                'id_player_creator', 'id_player_invited'
            ).get(id_match=pk)
        except MatchData.DoesNotExist:
            return Response({'error': 'Partido no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        if request.user.id not in {match.id_player_creator_id, match.id_player_invited_id}:
            return Response({'error': 'No sos participante de este partido.'}, status=status.HTTP_403_FORBIDDEN)

        if match.match_state not in {MatchState.INICIADO, MatchState.FINALIZADA}:
            return Response({'error': 'No se puede deshacer en este estado.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            match_score = match.match_score
        except MatchScore.DoesNotExist:
            return Response({'error': 'El partido no tiene marcador.'}, status=status.HTTP_400_BAD_REQUEST)

        last_point = MatchPoint.objects.filter(
            id_game__id_set__id_match_score=match_score
        ).order_by('-created_at').first()

        if not last_point:
            return Response({'error': 'No hay puntos para deshacer.'}, status=status.HTTP_400_BAD_REQUEST)

        game        = last_point.id_game
        current_set = game.id_set

        with transaction.atomic():
            last_point.delete()

            if game.winner_id_id is None:
                return Response({'mensaje': 'Punto deshecho.'}, status=status.HTTP_200_OK)

            # El punto eliminado cerraba un game — revertir
            game_winner_id  = game.winner_id_id
            set_was_closed  = current_set.winner_id_id is not None
            match_was_closed = match.match_state == MatchState.FINALIZADA

            # Revertir score del set
            if game_winner_id == match.id_player_creator_id:
                current_set.score_p1 = max(0, current_set.score_p1 - 1)
            else:
                current_set.score_p2 = max(0, current_set.score_p2 - 1)

            if set_was_closed:
                # Eliminar el nuevo set vacío que se creó al cerrar el set
                new_set = MatchSet.objects.filter(
                    id_match_score=match_score, winner_id__isnull=True
                ).order_by('-created_at').first()
                if new_set and not MatchPoint.objects.filter(id_game__id_set=new_set).exists():
                    MatchGame.objects.filter(id_set=new_set).delete()
                    new_set.delete()

                # Reabrir set
                current_set.winner_id = None
                current_set.duration  = None

                if match_was_closed:
                    match_score.winner_id = None
                    match_score.duration  = None
                    match_score.save()
                    match.match_state = MatchState.INICIADO
                    match.save()
            else:
                # Eliminar el nuevo game vacío que se creó al cerrar el game
                new_game = MatchGame.objects.filter(
                    id_set=current_set
                ).exclude(id_game=game.id_game).order_by('-created_at').first()
                if new_game and not MatchPoint.objects.filter(id_game=new_game).exists():
                    new_game.delete()

            current_set.save()

            # Reabrir game
            game.winner_id           = None
            game.duration            = None
            game.p1_game_final_score = None
            game.p2_game_final_score = None
            game.is_break            = None
            game.save()

        return Response({'mensaje': 'Punto deshecho.'}, status=status.HTTP_200_OK)


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
