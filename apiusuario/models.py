from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

class UsuarioManager(BaseUserManager):
    def create_user(self, correo, password=None, **extra_fields):
        if not correo: raise ValueError('El correo es obligatorio')
        correo = self.normalize_email(correo)
        user = self.model(correo=correo, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class RolUsuario(models.TextChoices):
    jugador = 'Jugador'
    entrenador = 'Entrenador'

class NivelUsuario(models.TextChoices):
    amateur = 'Amateur'
    semipro = 'Semi-Pro'
    pro = 'Profesional'

class SexoUsuario(models.TextChoices):
    masculino = 'Masculino', 'Masculino'
    femenino = 'Femenino', 'Femenino'
    otro = 'Otro', 'Otro'

class Usuario(AbstractBaseUser):
    nombre = models.CharField(max_length=100)
    apellidoPaterno = models.CharField(max_length=100)
    apellidoMaterno = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    rol = models.CharField(max_length=20, choices=RolUsuario.choices, default=RolUsuario.jugador)
    sexo = models.CharField(max_length=10, choices=SexoUsuario.choices, null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    altura = models.IntegerField(null=True, blank=True)
    peso = models.IntegerField(null=True, blank=True)
    nivelUsuario = models.CharField(max_length=20, choices=NivelUsuario.choices, null=True, blank=True)
    entrenador = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='jugadores'
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UsuarioManager()

    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = ['nombre']

    def __str__(self):
        return self.correo



class TokenSession(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='token_sessions')
    access_token = models.TextField()
    refresh_token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()  # Cuando expira el access token
    is_active = models.BooleanField(default=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.usuario.correo} - {self.created_at}"