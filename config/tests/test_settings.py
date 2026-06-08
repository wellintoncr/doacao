import importlib
import os
import sys

import pytest
from django.core.exceptions import ImproperlyConfigured


@pytest.fixture(autouse=True)
def _restore_settings_module():
    """Restaura o env e reimporta o config.settings pra voltar a refletir o .env real."""
    # as duas chaves sempre existem: a leitura do .env no import copia elas pro os.environ
    saved = {key: os.environ[key] for key in ("DEBUG", "SECRET_KEY")}
    yield
    os.environ.update(saved)
    import config.settings

    importlib.reload(config.settings)


def _reload_settings(monkeypatch, secret_key):
    monkeypatch.setenv("DEBUG", "off")
    monkeypatch.setenv("SECRET_KEY", secret_key)
    # simula um processo real (fora do pytest) pra passar também pelo branch do storage do whitenoise
    monkeypatch.delitem(sys.modules, "pytest")
    import config.settings

    return importlib.reload(config.settings)


def test_production_enables_security_hardening(monkeypatch):
    module = _reload_settings(monkeypatch, "a-strong-production-secret-key")
    assert module.DEBUG is False
    assert module.SECURE_SSL_REDIRECT is True
    assert module.SESSION_COOKIE_SECURE is True
    assert module.STORAGES["staticfiles"]["BACKEND"] == "whitenoise.storage.CompressedManifestStaticFilesStorage"


def test_production_rejects_placeholder_secret_key(monkeypatch):
    with pytest.raises(ImproperlyConfigured):
        _reload_settings(monkeypatch, "change-me-to-a-real-secret-key")
