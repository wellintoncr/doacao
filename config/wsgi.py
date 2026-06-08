"""
Config WSGI do projeto.

Expõe o callable WSGI como a variável ``application`` no nível do módulo.

Mais detalhes em
https://docs.djangoproject.com/en/6.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()
