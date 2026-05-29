from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


@database_sync_to_async
def get_user_from_token(token):
    from django.contrib.auth import get_user_model
    Usuario = get_user_model()
    try:
        validated = UntypedToken(token)
        user_id = validated['user_id']
        return Usuario.objects.get(id=user_id)
    except (InvalidToken, TokenError, Usuario.DoesNotExist):
        return AnonymousUser()


class JWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope['type'] == 'websocket':
            query_string = scope.get('query_string', b'').decode()
            params = parse_qs(query_string)
            token = params.get('token', [None])[0]
            scope['user'] = await get_user_from_token(token) if token else AnonymousUser()

        return await self.app(scope, receive, send)
