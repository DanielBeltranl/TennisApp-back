from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

class UsuarioManager(BaseUserManager):
    def create_user(self, correo, password=None, **extra_fields):
        if not correo: raise ValueError('El correo es obligatorio')
        correo = self.normalize_email(correo)
        user = self.model(correo=correo, **extra_fields)
        user.set_password(password) # Encripta automáticamente
        user.save(using=self._db)
        return user

class NivelUsuario(models.TextChoices):
    entrenador = 'Entrenador'
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
    sexo = models.CharField(max_length=10, choices=SexoUsuario.choices, default=SexoUsuario.otro)
    edad = models.IntegerField()
    altura = models.IntegerField()
    peso = models.IntegerField()
    nivelUsuario = models.CharField(max_length=20, choices=NivelUsuario.choices, default=NivelUsuario.amateur)
    
    # Requerido para Django Auth
    is_active = models.BooleanField(default=True)
    
    objects = UsuarioManager()

    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = ['nombre']


    def __str__(self):
        return self.correo
