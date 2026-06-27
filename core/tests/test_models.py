import pytest

from core.models import User


@pytest.mark.django_db
def test_user_str(user):
    assert str(user) == "voluntario@example.com"


@pytest.mark.django_db
def test_create_user_requires_email():
    with pytest.raises(ValueError):
        User.objects.create_user(email="", password="x", name="Alguém")


@pytest.mark.django_db
def test_create_user_normalizes_email_and_sets_password():
    user = User.objects.create_user(email="maria@EXAMPLE.COM", password="segredo-123", name="Maria")
    assert user.email == "maria@example.com"
    assert user.check_password("segredo-123")
    assert not user.is_staff


@pytest.mark.django_db
def test_create_superuser_sets_flags():
    admin = User.objects.create_superuser(email="admin@example.com", password="segredo-123", name="Admin")
    assert admin.is_staff
    assert admin.is_superuser
