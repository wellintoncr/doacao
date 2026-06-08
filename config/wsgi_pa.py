# Esse arquivo não é executado, fica só de referência
# É pra usar na configuração WSGI do PythonAnywhere
import os
import sys

from django.core.wsgi import get_wsgi_application

path = "/home/doacao/doacao"  # troca pro caminho real no PythonAnywhere
if path not in sys.path:
    sys.path.append(path)

os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"


application = get_wsgi_application()
