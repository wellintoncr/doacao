import pytest

from core.models import User


@pytest.fixture(autouse=True)
def _fast_password_hasher(settings):
    # hasher fraco de propósito: deixa a criação de usuários nos testes bem mais rápida
    settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


@pytest.fixture
def user(db):
    return User.objects.create_user(email="voluntario@example.com", password="senha-forte-123", name="Voluntário")


@pytest.fixture
def other_user(db):
    return User.objects.create_user(email="outra@example.com", password="senha-forte-123", name="Outra Pessoa")


@pytest.fixture
def auth_client(client, user):
    client.force_login(user)
    return client
