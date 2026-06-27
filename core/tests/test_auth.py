import pytest
from django.urls import reverse

from core.models import User


@pytest.mark.django_db
def test_login_page_shows_both_forms(client):
    response = client.get(reverse("login"))
    assert response.status_code == 200
    content = response.content.decode()
    assert "Já tenho conta" in content
    assert "Criar conta" in content


@pytest.mark.django_db
def test_login_success_redirects_to_board(client, user):
    response = client.post(
        reverse("login"),
        {"username": "voluntario@example.com", "password": "senha-forte-123"},
    )
    assert response.status_code == 302
    assert response.url == "/"


@pytest.mark.django_db
def test_login_wrong_password_shows_error(client, user):
    response = client.post(
        reverse("login"),
        {"username": "voluntario@example.com", "password": "errada"},
    )
    assert response.status_code == 200
    assert response.context["form"].non_field_errors()


@pytest.mark.django_db
def test_login_redirects_when_already_authenticated(auth_client):
    assert auth_client.get(reverse("login")).status_code == 302


@pytest.mark.django_db
def test_register_creates_account_and_logs_in(client):
    response = client.post(
        reverse("register"),
        {
            "name": "Maria",
            "email": "maria@example.com",
            "password1": "segredo-muito-bom-1",
            "password2": "segredo-muito-bom-1",
        },
    )
    assert response.status_code == 302
    assert response.url == reverse("event-detail")
    user = User.objects.get(email="maria@example.com")
    assert user.name == "Maria"
    # já sai logado: o perfil abre sem passar pelo login
    assert client.get(reverse("profile")).status_code == 200


@pytest.mark.django_db
def test_register_password_mismatch_rerenders(client):
    response = client.post(
        reverse("register"),
        {
            "name": "Maria",
            "email": "maria@example.com",
            "password1": "segredo-muito-bom-1",
            "password2": "diferente",
        },
    )
    assert response.status_code == 200
    assert response.context["register_form"].errors
    assert User.objects.count() == 0


@pytest.mark.django_db
def test_register_duplicate_email_rerenders(client, user):
    response = client.post(
        reverse("register"),
        {
            "name": "Outro",
            "email": "voluntario@example.com",
            "password1": "segredo-muito-bom-1",
            "password2": "segredo-muito-bom-1",
        },
    )
    assert response.status_code == 200
    assert "email" in response.context["register_form"].errors
    assert User.objects.count() == 1


@pytest.mark.django_db
def test_logout_redirects_to_login(auth_client):
    response = auth_client.post(reverse("logout"))
    assert response.status_code == 302
    assert response.url == reverse("login")
