import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_profile_page_renders(client):
    response = client.get(reverse("profile"))
    assert response.status_code == 200
    assert "Seu nome" in response.content.decode()


@pytest.mark.django_db
def test_navbar_links_to_profile(client, frozen_today):
    response = client.get(reverse("event-detail"))
    assert reverse("profile") in response.content.decode()


@pytest.mark.django_db
def test_board_loads_profile_guard(client, frozen_today):
    # o redirect em si é do lado do cliente; aqui só garantimos que o guard tá na página
    response = client.get(reverse("event-detail"))
    assert "js/profile-guard.js" in response.content.decode()


@pytest.mark.django_db
def test_item_card_uses_hidden_name_field(client, frozen_today, item):
    content = client.get(reverse("event-detail")).content.decode()
    assert 'type="hidden" name="person_name"' in content
    assert 'placeholder="Seu nome"' not in content
