from rest_framework.permissions import BasePermission


class EsJugador(BasePermission):
    def has_permission(self, request, view):
        return bool(request.auth and request.auth.get('rol') == 'Jugador')


class EsEntrenador(BasePermission):
    def has_permission(self, request, view):
        return bool(request.auth and request.auth.get('rol') == 'Entrenador')
