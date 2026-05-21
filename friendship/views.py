from django.db import connection, transaction
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import Friendship, FriendshipStatus
from .serializer import (
    PlayerSearchSerializer,
    SendFriendRequestSerializer,
    FriendshipSerializer,
)

Usuario = get_user_model()


class PlayerSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        term = request.query_params.get('term', '').strip()
        if not term:
            return Response([])

        like_param = f"%{term}%"

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    u.id AS player_id,
                    u.correo AS correo,
                    (u.nombre || ' ' || u."apellidoPaterno" || ' ' || u."apellidoMaterno") AS display_name,
                    u."nivelUsuario" AS nivel,
                    CASE
                        WHEN f.id IS NOT NULL AND f.status = 'ACEPTADO' THEN 'PARTNERS'
                        WHEN f.id IS NOT NULL AND f.status = 'PENDIENTE' THEN 'PENDING'
                        ELSE 'NONE'
                    END AS button_state
                FROM apiusuario_usuario u
                LEFT JOIN friendship f
                    ON f.user_id = %s AND f.friend_id = u.id
                WHERE (
                    LOWER(u.nombre) LIKE LOWER(%s)
                    OR LOWER(u."apellidoPaterno") LIKE LOWER(%s)
                    OR LOWER(u.correo) LIKE LOWER(%s)
                    OR LOWER(u.nombre || ' ' || u."apellidoPaterno") LIKE LOWER(%s)
                )
                AND u.id <> %s
                AND u.is_active = true
                LIMIT 15
            """, [request.user.id, like_param, like_param, like_param, like_param, request.user.id])

            columns = [col[0] for col in cursor.description]
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

        serializer = PlayerSearchSerializer(rows, many=True)
        return Response(serializer.data)


class SendFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SendFriendRequestSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        friend = Usuario.objects.get(id=serializer.validated_data['friend_id'])
        friendship = Friendship.objects.create(user=request.user, friend=friend)

        return Response(FriendshipSerializer(friendship).data, status=status.HTTP_201_CREATED)


class AcceptFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            friendship = Friendship.objects.get(id=pk, friend=request.user, status=FriendshipStatus.PENDIENTE)
        except Friendship.DoesNotExist:
            return Response({'error': 'Solicitud no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            friendship.status = FriendshipStatus.ACEPTADO
            friendship.save()

            Friendship.objects.create(
                user=request.user,
                friend=friendship.user,
                status=FriendshipStatus.ACEPTADO,
            )

        return Response(FriendshipSerializer(friendship).data)


class RejectFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            friendship = Friendship.objects.get(id=pk, friend=request.user, status=FriendshipStatus.PENDIENTE)
        except Friendship.DoesNotExist:
            return Response({'error': 'Solicitud no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        friendship.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PendingRequestsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        requests = Friendship.objects.filter(
            friend=request.user,
            status=FriendshipStatus.PENDIENTE
        ).select_related('user', 'friend')

        serializer = FriendshipSerializer(requests, many=True)
        return Response(serializer.data)


class FriendListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        friends = Friendship.objects.filter(
            user=request.user,
            status=FriendshipStatus.ACEPTADO
        ).select_related('user', 'friend')

        serializer = FriendshipSerializer(friends, many=True)
        return Response(serializer.data)


class RemoveFriendView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            friendship = Friendship.objects.get(id=pk, user=request.user, status=FriendshipStatus.ACEPTADO)
        except Friendship.DoesNotExist:
            return Response({'error': 'Amistad no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            Friendship.objects.filter(
                user=friendship.friend,
                friend=request.user,
                status=FriendshipStatus.ACEPTADO,
            ).delete()
            friendship.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
