import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_profile_requires_login(client):
    response = client.get(reverse("profile"))
    assert response.status_code == 302
    assert response.url.startswith(f"{reverse('login')}?next=")


@pytest.mark.django_db
def test_profile_shows_both_forms(auth_client, user):
    response = auth_client.get(reverse("profile"))
    assert response.status_code == 200
    assert response.context["name_form"].instance == user
    assert "Trocar senha" in response.content.decode()


@pytest.mark.django_db
def test_profile_updates_name(auth_client, user):
    response = auth_client.post(reverse("profile"), {"name": "Novo Nome"})
    assert response.status_code == 302
    user.refresh_from_db()
    assert user.name == "Novo Nome"


@pytest.mark.django_db
def test_profile_rejects_empty_name(auth_client, user):
    response = auth_client.post(reverse("profile"), {"name": ""})
    assert response.status_code == 200
    assert response.context["name_form"].errors
    user.refresh_from_db()
    assert user.name == "Voluntário"


@pytest.mark.django_db
def test_password_change(auth_client, user):
    response = auth_client.post(
        reverse("password-change"),
        {
            "old_password": "senha-forte-123",
            "new_password1": "outra-senha-boa-9",
            "new_password2": "outra-senha-boa-9",
        },
    )
    assert response.status_code == 302
    user.refresh_from_db()
    assert user.check_password("outra-senha-boa-9")
    # a sessão continua válida depois da troca (update_session_auth_hash)
    assert auth_client.get(reverse("profile")).status_code == 200


@pytest.mark.django_db
def test_password_change_wrong_old_password(auth_client):
    response = auth_client.post(
        reverse("password-change"),
        {
            "old_password": "errada",
            "new_password1": "outra-senha-boa-9",
            "new_password2": "outra-senha-boa-9",
        },
    )
    assert response.status_code == 200
    assert response.context["password_form"].errors
    # o template do perfil precisa dos dois formulários mesmo no erro
    assert "name_form" in response.context


@pytest.mark.django_db
def test_password_change_get_redirects_to_profile(auth_client):
    response = auth_client.get(reverse("password-change"))
    assert response.status_code == 302
    assert response.url == reverse("profile")
