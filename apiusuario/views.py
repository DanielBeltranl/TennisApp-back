from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializer import UsuarioSerializer
from .models import Usuario
from rest_framework import permissions

# Create your views here.

class UsuarioViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]