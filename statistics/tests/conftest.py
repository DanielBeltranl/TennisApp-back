"""
Django settings for pure unit tests of statistics/calculators.py.
No database is needed — all tests use in-memory fake objects.
"""
from django.conf import settings


def pytest_configure(config):
    if settings.configured:
        return
    settings.configure(
        SECRET_KEY='insecure-test-key-for-calculators',
        USE_TZ=True,
        INSTALLED_APPS=[],
        DATABASES={},
        TENNIS_DISTANCE_PARAMS={
            ('Amateur',     'Clay', 'Masculino'): {'effective': 23.0, 'mpm': 28.5},
            ('Amateur',     'Clay', 'Femenino'):  {'effective': 21.0, 'mpm': 25.0},
            ('Amateur',     'Hard', 'Masculino'): {'effective': 17.0, 'mpm': 34.0},
            ('Amateur',     'Hard', 'Femenino'):  {'effective': 13.0, 'mpm': 29.0},
            ('Semi-Pro',    'Clay', 'Masculino'): {'effective': 31.0, 'mpm': 36.0},
            ('Semi-Pro',    'Clay', 'Femenino'):  {'effective': 28.0, 'mpm': 31.5},
            ('Semi-Pro',    'Hard', 'Masculino'): {'effective': 22.0, 'mpm': 43.0},
            ('Semi-Pro',    'Hard', 'Femenino'):  {'effective': 20.0, 'mpm': 38.0},
            ('Profesional', 'Clay', 'Masculino'): {'effective': 40.0, 'mpm': 40.0},
            ('Profesional', 'Clay', 'Femenino'):  {'effective': 35.0, 'mpm': 37.0},
            ('Profesional', 'Hard', 'Masculino'): {'effective': 27.0, 'mpm': 48.5},
            ('Profesional', 'Hard', 'Femenino'):  {'effective': 25.0, 'mpm': 44.0},
        },
    )
