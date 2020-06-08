"""WSGI config for Novizi project."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "novizi.settings")

application = get_wsgi_application()
