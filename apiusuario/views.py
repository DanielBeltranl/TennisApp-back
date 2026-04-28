from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializer import UsuarioSerializer
from .models import Usuario
from rest_framework import permissions

# Create your views here.

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.AllowAny]
