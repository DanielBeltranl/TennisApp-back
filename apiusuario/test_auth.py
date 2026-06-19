"""
Test plan — User management, Authentication and JWT (EP3).

Scope (responsibilities under test):
  - User registration (player and coach) and its validations.
  - Login / token issuance with custom claims.
  - JWT-protected endpoints, session lifecycle (login, logout, re-login),
    password change and active-session listing.

Run in isolation:
    python manage.py test apiusuario.test_auth --settings=back.settings_test
"""

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from apiusuario.models import Usuario, TokenSession

REGISTRO_URL = '/api/usuarios/registro/'
LOGIN_URL = '/api/login/'
PERFIL_URL = '/api/usuarios/perfil/'
CAMBIAR_PASSWORD_URL = '/api/usuarios/cambiar_password/'
LOGOUT_URL = '/api/usuarios/logout/'
SESIONES_URL = '/api/usuarios/sesiones_activas/'

PLAYER_PAYLOAD = {
    'nombre': 'Juan',
    'apellidoPaterno': 'Perez',
    'apellidoMaterno': 'Gonzalez',
    'correo': 'juan@test.com',
    'password': 'Clave1234!',
    'rol': 'Jugador',
    'sexo': 'Masculino',
    'fecha_nacimiento': '2000-01-15',
    'altura': 180,
    'peso': 75,
}

COACH_PAYLOAD = {
    'nombre': 'Carlos',
    'apellidoPaterno': 'Diaz',
    'apellidoMaterno': 'Munoz',
    'correo': 'carlos@test.com',
    'password': 'Clave1234!',
    'rol': 'Entrenador',
    'fecha_nacimiento': '1985-03-20',
}


def _payload(base, **overrides):
    data = dict(base)
    data.update(overrides)
    return data


def _payload_without(base, *fields):
    data = dict(base)
    for field in fields:
        data.pop(field, None)
    return data


class RegistroJugadorTests(APITestCase):
    """CP-REG-* — Registration of players and field validation."""

    def test_cp_reg_01_registro_jugador_completo(self):
        resp = self.client.post(REGISTRO_URL, _payload(PLAYER_PAYLOAD), format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', resp.data)
        self.assertIn('refresh', resp.data)
        self.assertEqual(resp.data['usuario']['correo'], 'juan@test.com')

    def test_cp_reg_02_falta_sexo(self):
        resp = self.client.post(REGISTRO_URL, _payload_without(PLAYER_PAYLOAD, 'sexo'), format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('sexo', resp.data)

    def test_cp_reg_03_falta_peso(self):
        resp = self.client.post(REGISTRO_URL, _payload_without(PLAYER_PAYLOAD, 'peso'), format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cp_reg_04_falta_altura(self):
        resp = self.client.post(REGISTRO_URL, _payload_without(PLAYER_PAYLOAD, 'altura'), format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cp_reg_05_correo_duplicado(self):
        self.client.post(REGISTRO_URL, _payload(PLAYER_PAYLOAD), format='json')
        resp = self.client.post(REGISTRO_URL, _payload(PLAYER_PAYLOAD), format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('correo', resp.data)

    def test_cp_reg_06_rol_invalido(self):
        resp = self.client.post(REGISTRO_URL, _payload(PLAYER_PAYLOAD, rol='Arbitro'), format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('rol', resp.data)

    def test_cp_reg_07_password_no_se_expone(self):
        resp = self.client.post(REGISTRO_URL, _payload(PLAYER_PAYLOAD), format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('password', resp.data['usuario'])

    def test_cp_reg_08_crea_token_session(self):
        resp = self.client.post(REGISTRO_URL, _payload(PLAYER_PAYLOAD), format='json')
        usuario = Usuario.objects.get(correo='juan@test.com')
        self.assertEqual(
            TokenSession.objects.filter(usuario=usuario, is_active=True).count(), 1
        )


class RegistroEntrenadorTests(APITestCase):
    """CP-REG-* — Registration of coaches."""

    def test_cp_reg_09_registro_entrenador_completo(self):
        resp = self.client.post(REGISTRO_URL, _payload(COACH_PAYLOAD), format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['usuario']['rol'], 'Entrenador')

    def test_cp_reg_10_entrenador_sin_fecha_nacimiento(self):
        # Expected behaviour: fecha_nacimiento is mandatory for coaches -> HTTP 400.
        resp = self.client.post(
            REGISTRO_URL, _payload_without(COACH_PAYLOAD, 'fecha_nacimiento'), format='json'
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('fecha_nacimiento', resp.data)


class LoginTests(APITestCase):
    """CP-LOGIN-* — Token issuance."""

    def setUp(self):
        self.client.post(REGISTRO_URL, _payload(PLAYER_PAYLOAD), format='json')

    def test_cp_login_01_credenciales_validas(self):
        resp = self.client.post(
            LOGIN_URL, {'correo': 'juan@test.com', 'password': 'Clave1234!'}, format='json'
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', resp.data)
        self.assertIn('refresh', resp.data)

    def test_cp_login_02_password_incorrecta(self):
        resp = self.client.post(
            LOGIN_URL, {'correo': 'juan@test.com', 'password': 'mala'}, format='json'
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cp_login_03_correo_inexistente(self):
        resp = self.client.post(
            LOGIN_URL, {'correo': 'nadie@test.com', 'password': 'Clave1234!'}, format='json'
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cp_login_04_claims_personalizados_en_jwt(self):
        resp = self.client.post(
            LOGIN_URL, {'correo': 'juan@test.com', 'password': 'Clave1234!'}, format='json'
        )
        payload = AccessToken(resp.data['access'])
        self.assertEqual(payload['correo'], 'juan@test.com')
        self.assertEqual(payload['nombre'], 'Juan')
        self.assertEqual(payload['rol'], 'Jugador')

    def test_cp_login_05_crea_token_session(self):
        self.client.post(
            LOGIN_URL, {'correo': 'juan@test.com', 'password': 'Clave1234!'}, format='json'
        )
        usuario = Usuario.objects.get(correo='juan@test.com')
        self.assertTrue(TokenSession.objects.filter(usuario=usuario, is_active=True).exists())

    def test_cp_login_06_relogin_invalida_sesion_anterior(self):
        for _ in range(2):
            self.client.post(
                LOGIN_URL, {'correo': 'juan@test.com', 'password': 'Clave1234!'}, format='json'
            )
        usuario = Usuario.objects.get(correo='juan@test.com')
        self.assertEqual(
            TokenSession.objects.filter(usuario=usuario, is_active=True).count(), 1
        )


class JWTProtegidoTests(APITestCase):
    """CP-JWT-* — Protected endpoints and session lifecycle."""

    def setUp(self):
        reg = self.client.post(REGISTRO_URL, _payload(PLAYER_PAYLOAD), format='json')
        self.access = reg.data['access']
        self.usuario = Usuario.objects.get(correo='juan@test.com')

    def _auth(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access}')

    def test_cp_jwt_01_perfil_sin_token(self):
        resp = self.client.post(PERFIL_URL)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cp_jwt_02_perfil_con_token(self):
        self._auth()
        resp = self.client.post(PERFIL_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['correo'], 'juan@test.com')

    def test_cp_jwt_03_token_malformado(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer token.falso.aqui')
        resp = self.client.post(PERFIL_URL)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cp_jwt_04_cambiar_password_correcto(self):
        self._auth()
        resp = self.client.post(
            CAMBIAR_PASSWORD_URL,
            {'password_actual': 'Clave1234!', 'password_nuevo': 'NuevaClave99!'},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_cp_jwt_05_cambiar_password_actual_incorrecta(self):
        self._auth()
        resp = self.client.post(
            CAMBIAR_PASSWORD_URL,
            {'password_actual': 'mala', 'password_nuevo': 'NuevaClave99!'},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cp_jwt_06_sesiones_activas(self):
        self._auth()
        resp = self.client.get(SESIONES_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(resp.data['total'], 1)

    def test_cp_jwt_07_logout_elimina_sesion(self):
        self._auth()
        resp = self.client.post(LOGOUT_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertFalse(
            TokenSession.objects.filter(access_token=self.access, is_active=True).exists()
        )
