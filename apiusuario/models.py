from django.db import models

class NivelUsuario(models.TextChoices):
    entrenador = 'Entrenador'
    amateur = 'Amateur'
    semipro = 'Semi-Pro'
    pro = 'Profesional'
    
class SexoUsuario(models.TextChoices):
    masculino = 'Masculino'
    femenino = 'Femenino'
    otro = 'Otro'

class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    apellidoPaterno = models.CharField(max_length=100)
    apellidoMaterno = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    contraseña = models.CharField(max_length=255)
    sexo = models.CharField(max_length=10, choices=SexoUsuario.choices, default=SexoUsuario.otro)
    edad = models.IntegerField()
    altura = models.IntegerField()
    peso = models.IntegerField()
    nivelUsuario = models.CharField(max_length=20, choices=NivelUsuario.choices, default=NivelUsuario.amateur)
    
    def __str__(self):
        return f"{self.nombre} {self.apellidoPaterno}"