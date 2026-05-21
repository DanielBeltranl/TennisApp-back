# TennisApp Backend

API REST para la aplicación TennisApp desarrollada con Django y Django REST Framework. Este backend proporciona autenticación JWT y gestión de usuarios para la plataforma de tenis.

---

## 📋 Tabla de Contenidos

- [Tecnologías Utilizadas](#-tecnologías-utilizadas)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación](#-instalación)
- [Configuración del Entorno](#-configuración-del-entorno)
- [Ejecutar el Servidor](#-ejecutar-el-servidor)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [API Endpoints](#-api-endpoints)
- [Autenticación JWT](#-autenticación-jwt)
- [Base de Datos](#-base-de-datos)
- [Notas Importantes](#-notas-importantes)

---

## 🛠️ Tecnologías Utilizadas

- **Django 5.2**: Framework web de Python para desarrollo rápido
- **Django REST Framework (DRF)**: Herramienta para construir APIs REST en Django
- **Django REST Framework SimpleJWT**: Autenticación con tokens JWT (JSON Web Tokens)
- **PostgreSQL**: Base de datos relacional
- **django-cors-headers**: Soporte para CORS (Cross-Origin Resource Sharing)
- **python-dotenv**: Gestión de variables de entorno
- **psycopg2-binary**: Adaptador PostgreSQL para Python
- **UV**: Gestor de paquetes y entornos de Python

---

## 📦 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

1. **Python 3.12+** - [Descargar](https://www.python.org/downloads/)
2. **UV** - Gestor de paquetes de Python (opcional pero recomendado)
   ```bash
   pip install uv
   ```
3. **Git** - Control de versiones
4. **Acceso a Base de Datos PostgreSQL** - Base de datos local o remota

---

## 🚀 Instalación

### Paso 1: Clonar el Repositorio

```bash
git clone <url-del-repositorio>
cd TennisApp-back
```

### Paso 2: Crear el Entorno Virtual

**Opción A - Usando UV (Recomendado):**
```bash
uv venv
```

**Opción B - Usando venv de Python:**
```bash
python -m venv .venv
```

### Paso 3: Activar el Entorno Virtual

**En Windows (PowerShell):**
```bash
.venv\Scripts\Activate.ps1
```

**En Windows (CMD):**
```bash
.venv\Scripts\activate.bat
```

**En macOS/Linux:**
```bash
source .venv/bin/activate
```

### Paso 4: Instalar Dependencias

**Usando UV:**
```bash
uv pip install -e .
```

**Usando pip:**
```bash
pip install django-cors-headers>=4.9.0 djangorestframework-simplejwt>=5.5.1 psycopg2-binary>=2.9.12 python-dotenv>=1.2.2
```

---

## 🔐 Configuración del Entorno

### Crear archivo `.env`

En la raíz del proyecto, crea un archivo `.env` con las siguientes variables:

```env
# Base de Datos PostgreSQL
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=tu_contraseña_segura
DB_HOST=localhost
DB_PORT=5432

# Django Settings
SECRET_KEY=tu_clave_secreta_django
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## 🗄️ Configuración de Base de Datos

### Ejecutar Migraciones

Una vez configurado el archivo `.env`, ejecuta las migraciones para crear las tablas:

```bash
uv run manage.py migrate
```

O sin UV:
```bash
python manage.py migrate
```

Este comando creará todas las tablas necesarias, incluyendo:
- `apiusuario_usuario` - Tabla de usuarios

---

## ▶️ Ejecutar el Servidor

### Iniciar el Servidor de Desarrollo

```bash
uv run manage.py runserver
```

El servidor estará disponible en:
- **URL Local**: `http://127.0.0.1:8000`
- **URL de Red**: `http://localhost:8000`

### Panel de Administración

Accede al panel admin en:
```
http://localhost:8000/admin/
```

---

## 📁 Estructura del Proyecto

```
TennisApp-back/
├── apiusuario/                           # App de gestión de usuarios
│   ├── migrations/                       # Migraciones de base de datos
│   │   ├── 0001_initial.py
│   │   ├── 0002_remove_usuario_tipousuario_usuario_nivelusuario.py
│   │   ├── 0003_remove_usuario_contraseña_usuario_last_login_and_more.py
│   │   └── 0004_remove_usuario_last_login_remove_usuario_password_and_more.py
│   ├── admin.py                         # Configuración del admin
│   ├── apps.py                          # Configuración de la app
│   ├── models.py                        # Modelos de datos (Usuario)
│   ├── serializer.py                    # Serializadores DRF
│   ├── tests.py                         # Tests unitarios
│   ├── urls.py                          # Rutas de la app
│   └── views.py                         # Vistas/controladores
├── back/                                 # Configuración principal del proyecto
│   ├── settings.py                      # Configuración de Django
│   ├── urls.py                          # Rutas principales
│   ├── asgi.py                          # Interfaz ASGI
│   └── wsgi.py                          # Interfaz WSGI
├── .env                                 # Variables de entorno (no commitear)
├── .env.example                         # Plantilla de variables de entorno
├── manage.py                            # Script de gestión de Django
├── pyproject.toml                       # Configuración de dependencias
├── uv.lock                              # Archivo de bloqueo de dependencias
└── README.md                            # Este archivo
```

---

## 🔌 API Endpoints

### Autenticación JWT

#### Obtener Token (Login)
```http
POST /api/token/
Content-Type: application/json

{
  "correo": "usuario@example.com",
  "password": "contraseña"
}
```

**Respuesta (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Refrescar Token
```http
POST /api/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Verificar Token
```http
POST /api/token/verify/
Content-Type: application/json

{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Gestión de Usuarios

#### Listar Usuarios
```http
GET /api/usuarios/
Authorization: Bearer <access_token>
```

**Respuesta (200 OK):**
```json
[
  {
    "id": 1,
    "nombre": "Juan",
    "apellidoPaterno": "García",
    "apellidoMaterno": "López",
    "correo": "juan@example.com",
    "sexo": "Masculino",
    "edad": 25,
    "altura": 180,
    "peso": 75,
    "nivelUsuario": "Amateur"
  }
]
```

#### Crear Usuario
```http
POST /api/usuarios/
Content-Type: application/json

{
  "nombre": "Juan",
  "apellidoPaterno": "García",
  "apellidoMaterno": "López",
  "correo": "juan@example.com",
  "password": "contraseña123",
  "sexo": "Masculino",
  "edad": 25,
  "altura": 180,
  "peso": 75,
  "nivelUsuario": "Amateur"
}
```

#### Obtener Usuario por ID
```http
GET /api/usuarios/{id}/
Authorization: Bearer <access_token>
```

#### Actualizar Usuario
```http
PUT /api/usuarios/{id}/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "nombre": "Juan",
  "apellidoPaterno": "García",
  "apellidoMaterno": "López",
  "sexo": "Masculino",
  "edad": 26,
  "altura": 181,
  "peso": 76
}
```

#### Eliminar Usuario
```http
DELETE /api/usuarios/{id}/
Authorization: Bearer <access_token>
```

---

## 🔐 Autenticación JWT

### ¿Cómo funciona?

1. El cliente envía credenciales (correo y contraseña) al endpoint `/api/token/`
2. El servidor valida las credenciales y devuelve dos tokens:
   - **access_token**: Usado para autenticar solicitudes (válido 5 minutos)
   - **refresh_token**: Usado para obtener un nuevo access_token (válido 24 horas)

### Usar el Token en Solicitudes

Incluye el token en el header `Authorization`:

```http
GET /api/usuarios/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Refrescar Token Expirado

Cuando el access_token expire, usa el refresh_token:

```bash
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."}'
```

---

## 🗄️ Base de Datos

### Modelo Usuario

```python
class Usuario(AbstractBaseUser):
    nombre = CharField(max_length=100)              # Nombre del usuario
    apellidoPaterno = CharField(max_length=100)     # Apellido paterno
    apellidoMaterno = CharField(max_length=100)     # Apellido materno
    correo = EmailField(unique=True)                # Email único
    sexo = CharField(choices=['Masculino', 'Femenino', 'Otro'])  # Sexo
    edad = IntegerField()                           # Edad en años
    altura = IntegerField()                         # Altura en cm
    peso = IntegerField()                           # Peso en kg
    nivelUsuario = CharField(choices=['Entrenador', 'Amateur', 'Semi-Pro', 'Profesional'])
    is_active = BooleanField(default=True)          # Estado de la cuenta
```

### Niveles de Usuario

- **Entrenador**: Usuarios entrenadores de tenis
- **Amateur**: Jugadores aficionados
- **Semi-Pro**: Jugadores semi-profesionales
- **Profesional**: Jugadores profesionales

---

## 📝 Notas Importantes

### ⚠️ Seguridad en Desarrollo vs Producción

**PRODUCCIÓN:**
- Cambia todas las contraseñas
- Genera una nueva `SECRET_KEY` con: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`
- Establece `DEBUG=False`
- Añade dominios reales a `ALLOWED_HOSTS`
- Usa HTTPS en lugar de HTTP

### 🔄 Flujo de Trabajo Colaborativo

1. **Clonar repositorio**
   ```bash
   git clone <url>
   cd TennisApp-back
   ```

2. **Crear rama de trabajo**
   ```bash
   git checkout -b feature/mi-funcionalidad
   ```

3. **Activar entorno virtual**
   ```bash
   .venv\Scripts\Activate.ps1  # Windows PowerShell
   ```

4. **Instalar dependencias**
   ```bash
   uv pip install -e .
   ```

5. **Configurar `.env`** (con credenciales compartidas)

6. **Ejecutar migraciones**
   ```bash
   uv run manage.py migrate
   ```

7. **Iniciar servidor**
   ```bash
   uv run manage.py runserver
   ```

8. **Hacer cambios y testing**

9. **Commitear cambios**
   ```bash
   git add .
   git commit -m "Descripción clara del cambio"
   git push origin feature/mi-funcionalidad
   ```

### 🆘 Troubleshooting

**Error: `ModuleNotFoundError: No module named 'rest_framework'`**
- Solución: Ejecuta `uv pip install djangorestframework djangorestframework-simplejwt`

**Error: `ModuleNotFoundError: No module named 'api'`**
- Solución: Verifica que las rutas en `back/urls.py` usen `apiusuario` no `api`

**Error: `Migration apiusuario references nonexistent parent node`**
- Solución: Actualiza los nombres de la app en los archivos de migración

**Error de conexión a base de datos**
- Verifica que el archivo `.env` tenga las credenciales correctas
- Comprueba la conectividad a PostgreSQL
- Asegúrate de que `DB_HOST`, `DB_USER`, `DB_PASSWORD` sean correctos

---
