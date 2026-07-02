from datetime import date

import pytest
from django.urls import reverse

from donation.models import Event, Pledge

HTMX = {"HX-Request": "true"}


@pytest.mark.django_db
def test_event_detail_defaults_to_first_sunday(auth_client, frozen_today):
    response = auth_client.get(reverse("event-detail"))
    assert response.status_code == 200
    assert response.context["selected"] == date(2025, 9, 14)
    assert response.context["sundays"] == [date(2025, 9, 14), date(2025, 9, 21), date(2025, 9, 28)]


@pytest.mark.django_db
def test_event_detail_selects_requested_sunday(auth_client, frozen_today):
    response = auth_client.get(reverse("event-detail"), {"date": "2025-09-21"})
    assert response.context["selected"] == date(2025, 9, 21)


@pytest.mark.django_db
def test_event_detail_falls_back_on_invalid_date(auth_client, frozen_today):
    response = auth_client.get(reverse("event-detail"), {"date": "garbage"})
    assert response.context["selected"] == date(2025, 9, 14)


@pytest.mark.django_db
def test_event_detail_without_items(auth_client, frozen_today):
    response = auth_client.get(reverse("event-detail"))
    assert response.context["summaries"] == []


@pytest.mark.django_db
def test_event_detail_shows_pledges_with_account_name(auth_client, frozen_today, pledge):
    response = auth_client.get(reverse("event-detail"))
    summary = response.context["summaries"][0]
    assert summary["total"] == 10
    assert "Voluntário" in response.content.decode()


@pytest.mark.django_db
def test_own_pledge_shows_controls(auth_client, frozen_today, pledge):
    content = auth_client.get(reverse("event-detail")).content.decode()
    assert "Editar" in content
    assert "Remover" in content


@pytest.mark.django_db
def test_foreign_pledge_hides_controls(auth_client, frozen_today, pledge, other_user):
    pledge.user = other_user
    pledge.save(update_fields=["user"])
    content = auth_client.get(reverse("event-detail")).content.decode()
    assert "Outra Pessoa" in content  # a doação aparece pra todo mundo
    assert "Editar" not in content  # mas só o autor vê os controles
    assert "Remover" not in content


@pytest.mark.django_db
def test_pledge_create_creates_event_lazily(auth_client, user, frozen_today, item):
    response = auth_client.post(
        reverse("pledge-add", args=[item.pk]),
        {"date": "2025-09-21", "quantity": 40},
    )
    assert response.status_code == 302
    assert response.url == f"{reverse('event-detail')}?date=2025-09-21"
    pledge = Pledge.objects.get()
    assert pledge.event.date == date(2025, 9, 21)
    assert pledge.user == user


@pytest.mark.django_db
def test_pledge_create_reuses_existing_event(auth_client, frozen_today, event, item):
    auth_client.post(
        reverse("pledge-add", args=[item.pk]),
        {"date": "2025-09-14", "quantity": 5},
    )
    assert Event.objects.count() == 1
    assert event.pledges.count() == 1


@pytest.mark.django_db
def test_pledge_create_htmx_returns_item_card(auth_client, frozen_today, item):
    response = auth_client.post(
        reverse("pledge-add", args=[item.pk]),
        {"date": "2025-09-14", "quantity": 5},
        headers=HTMX,
    )
    assert response.status_code == 200
    assert "donation/partials/item_card.html" in [t.name for t in response.templates]
    assert "Voluntário" in response.content.decode()


@pytest.mark.django_db
def test_pledge_create_htmx_invalid_shows_errors(auth_client, frozen_today, item):
    response = auth_client.post(
        reverse("pledge-add", args=[item.pk]),
        {"date": "2025-09-14", "quantity": 0},
        headers=HTMX,
    )
    assert response.status_code == 200
    assert response.context["form"].errors
    assert Pledge.objects.count() == 0


@pytest.mark.django_db
def test_pledge_create_invalid_without_htmx_redirects(auth_client, frozen_today, item):
    response = auth_client.post(
        reverse("pledge-add", args=[item.pk]),
        {"date": "2025-09-14", "quantity": 0},
    )
    assert response.status_code == 302
    assert Pledge.objects.count() == 0


@pytest.mark.django_db
def test_pledge_create_rejects_closed_date(auth_client, frozen_today, item):
    # domingo fora do horizonte configurado ainda não tá aberto pra doações
    response = auth_client.post(
        reverse("pledge-add", args=[item.pk]),
        {"date": "2025-10-05", "quantity": 5},
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_pledge_create_rejects_inactive_item(auth_client, frozen_today, item):
    item.is_active = False
    item.save(update_fields=["is_active"])
    response = auth_client.post(
        reverse("pledge-add", args=[item.pk]),
        {"date": "2025-09-14", "quantity": 5},
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_pledge_edit_page(auth_client, frozen_today, pledge):
    response = auth_client.get(reverse("pledge-edit", args=[pledge.pk]))
    assert response.status_code == 200
    assert response.context["form"].instance == pledge


@pytest.mark.django_db
def test_pledge_edit_updates_pledge(auth_client, frozen_today, pledge):
    response = auth_client.post(
        reverse("pledge-edit", args=[pledge.pk]),
        {"quantity": 25},
    )
    assert response.status_code == 302
    pledge.refresh_from_db()
    assert pledge.quantity == 25


@pytest.mark.django_db
def test_pledge_edit_invalid_rerenders_form(auth_client, frozen_today, pledge):
    response = auth_client.post(
        reverse("pledge-edit", args=[pledge.pk]),
        {"quantity": 0},
    )
    assert response.status_code == 200
    assert response.context["form"].errors


@pytest.mark.django_db
def test_pledge_edit_denied_for_other_user(auth_client, frozen_today, pledge, other_user):
    pledge.user = other_user
    pledge.save(update_fields=["user"])
    assert auth_client.get(reverse("pledge-edit", args=[pledge.pk])).status_code == 404
    assert auth_client.post(reverse("pledge-edit", args=[pledge.pk]), {"quantity": 99}).status_code == 404


@pytest.mark.django_db
def test_pledge_delete(auth_client, frozen_today, pledge):
    response = auth_client.post(reverse("pledge-delete", args=[pledge.pk]))
    assert response.status_code == 302
    assert Pledge.objects.count() == 0


@pytest.mark.django_db
def test_pledge_delete_htmx_returns_item_card(auth_client, frozen_today, pledge):
    response = auth_client.post(reverse("pledge-delete", args=[pledge.pk]), headers=HTMX)
    assert response.status_code == 200
    assert "donation/partials/item_card.html" in [t.name for t in response.templates]
    assert Pledge.objects.count() == 0


@pytest.mark.django_db
def test_pledge_delete_denied_for_other_user(auth_client, frozen_today, pledge, other_user):
    pledge.user = other_user
    pledge.save(update_fields=["user"])
    assert auth_client.post(reverse("pledge-delete", args=[pledge.pk])).status_code == 404
    assert Pledge.objects.count() == 1


@pytest.mark.django_db
def test_board_requires_login(client, frozen_today):
    response = client.get(reverse("event-detail"))
    assert response.status_code == 302
    assert response.url.startswith(f"{reverse('login')}?next=")


@pytest.mark.django_db
def test_pledge_endpoints_require_login(client, frozen_today, pledge):
    login = reverse("login")
    assert client.post(reverse("pledge-add", args=[pledge.item.pk]), {}).url.startswith(f"{login}?next=")
    assert client.get(reverse("pledge-edit", args=[pledge.pk])).url.startswith(f"{login}?next=")
    assert client.post(reverse("pledge-delete", args=[pledge.pk])).url.startswith(f"{login}?next=")


@pytest.mark.django_db
def test_board_content_details(auth_client, frozen_today, item):
    content = auth_client.get(reverse("event-detail")).content.decode()
    # navbar mostra o nome da conta; o formulário só pede quantidade
    assert "Perfil · Voluntário" in content
    assert 'name="person_name"' not in content
    assert "profile-guard" not in content
