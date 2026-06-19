"""
Test settings — isolated environment for the user-management / auth / JWT suite.

Rationale: the production settings target PostgreSQL (Neon) and Redis. Unit tests
must not depend on external infrastructure, so this module:
  - swaps the database for an in-memory SQLite engine,
  - trims INSTALLED_APPS to only what the auth module needs (this also avoids the
    name clash between the project's `statistics` app and Python's stdlib module),
  - points ROOT_URLCONF at a minimal urlconf (back.urls_test).

Run with:
    python manage.py test apiusuario.test_auth --settings=back.settings_test
"""

# ---------------------------------------------------------------------------
# Pin the real stdlib `statistics` module.
#
# The project ships an app literally named `statistics`, whose folder sits on
# sys.path and therefore shadows Python's stdlib `statistics` for *any*
# `import statistics`. Django's sqlite3 backend imports the stdlib one
# (it needs `statistics.pstdev` for aggregate functions), so without this the
# test database fails to load. The proper long-term fix is to rename the app
# (e.g. `player_stats`); this shim only scopes the workaround to the test run.
# ---------------------------------------------------------------------------
import importlib.util as _ilu
import os as _os
import sys as _sys
import sysconfig as _sysconfig

if not hasattr(_sys.modules.get('statistics'), 'pstdev'):
    _stdlib_statistics = _os.path.join(_sysconfig.get_paths()['stdlib'], 'statistics.py')
    _spec = _ilu.spec_from_file_location('statistics', _stdlib_statistics)
    _module = _ilu.module_from_spec(_spec)
    _spec.loader.exec_module(_module)
    _sys.modules['statistics'] = _module

from .settings import *  # noqa: E402,F401,F403

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'apiusuario',
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
]

ROOT_URLCONF = 'back.urls_test'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Auth tests never touch websockets; drop the Redis channel layer entirely.
CHANNEL_LAYERS = {}

# Speed up password hashing during tests.
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
