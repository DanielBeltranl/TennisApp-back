# Plan de Implementación: Buscador Global de Jugadores (DRF + PostgreSQL)

## Contexto

Endpoint de búsqueda global de usuarios con Django REST Framework y SQL nativo sobre PostgreSQL, adaptado al modelo personalizado `Usuario`.

Las relaciones activas usan el **Enfoque Duplicado/Simétrico**: si dos usuarios son partners, existen dos registros en la tabla intermedia: `(A, B)` y `(B, A)`.

---

## Reglas de Ejecución Obligatorias

1. **Prohibido usar el ORM de Django** (`.filter`, `.raw`, etc.) en la vista de búsqueda. Solo cursores directos.
2. **Usar parametrización nativa** (`%s`) para prevenir inyección SQL en PostgreSQL.
3. **No agregar comentarios explicativos** en el código fuente generado.

---

## Paso 1 — Modelo de Relaciones (`relation_management/models.py`)

Agregar el modelo `Friendship`:

```python
class Friendship(models.Model):
    user = models.ForeignKey(
        'relation_management.Usuario',
        on_delete=models.CASCADE,
        related_name='friendships_initiated'
    )
    friend = models.ForeignKey(
        'relation_management.Usuario',
        on_delete=models.CASCADE,
        related_name='friendships_received'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'friend')
```

Luego ejecutar:

```bash
python manage.py makemigrations relation_management
python manage.py migrate
```

---

## Paso 2 — Serializer de Salida (`serializers.py`)

```python
class PlayerSearchSerializer(serializers.Serializer):
    player_id = serializers.IntegerField()
    correo = serializers.EmailField()
    display_name = serializers.CharField()
    nivel = serializers.CharField()
    button_state = serializers.SerializerMethodField()

    def get_button_state(self, obj):
        if obj.get('friendship_exists') == 1:
            return "PARTNERS"
        return "NONE"
```

---

## Paso 3 — API View con SQL Nativo (`views.py`)

```python
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

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
                    CASE WHEN f.id IS NOT NULL THEN 1 ELSE 0 END AS friendship_exists
                FROM relation_management_usuario u
                LEFT JOIN relation_management_friendship f 
                    ON f.user_id = %s AND f.friend_id = u.id
                WHERE 
                    (
                        LOWER(u.nombre) LIKE LOWER(%s) 
                        OR LOWER(u."apellidoPaterno") LIKE LOWER(%s) 
                        OR LOWER(u.correo) LIKE LOWER(%s)
                        OR LOWER(u.nombre || ' ' || u."apellidoPaterno") LIKE LOWER(%s)
                    )
                    AND u.id <> %s
                LIMIT 15;
            """, [request.user.id, like_param, like_param, like_param, like_param, request.user.id])

            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        serializer = PlayerSearchSerializer(data, many=True)
        return Response(serializer.data)
```

---

## Paso 4 — Enrutamiento (`urls.py`)

```python
from django.urls import path
from .views import PlayerSearchView

urlpatterns = [
    path('api/players/search/', PlayerSearchView.as_view()),
]
```
