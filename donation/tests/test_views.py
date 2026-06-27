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
def test_event_detail_shows_pledges(auth_client, frozen_today, pledge):
    response = auth_client.get(reverse("event-detail"))
    summary = response.context["summaries"][0]
    assert summary["total"] == 10
    assert "John" in response.content.decode()


@pytest.mark.django_db
def test_pledge_create_creates_event_lazily(auth_client, frozen_today, item):
    response = auth_client.post(
        reverse("pledge-add", args=[item.pk]),
        {"date": "2025-09-21", "quantity": 40, "person_name": "Jane"},
    )
    assert response.status_code == 302
    assert response.url == f"{reverse('event-detail')}?date=2025-09-21"
    pledge = Pledge.objects.get()
    assert pledge.event.date == date(2025, 9, 21)


@pytest.mark.django_db
def test_pledge_create_reuses_existing_event(auth_client, frozen_today, event, item):
    auth_client.post(
        reverse("pledge-add", args=[item.pk]),
        {"date": "2025-09-14", "quantity": 5, "person_name": "Jane"},
    )
    assert Event.objects.count() == 1
    assert event.pledges.count() == 1


@pytest.mark.django_db
def test_pledge_create_htmx_returns_item_card(auth_client, frozen_today, item):
    response = auth_client.post(
        reverse("pledge-add", args=[item.pk]),
        {"date": "2025-09-14", "quantity": 5, "person_name": "Jane"},
        headers=HTMX,
    )
    assert response.status_code == 200
    assert "donation/partials/item_card.html" in [t.name for t in response.templates]
    assert "Jane" in response.content.decode()


@pytest.mark.django_db
def test_pledge_create_htmx_invalid_shows_errors(auth_client, frozen_today, item):
    response = auth_client.post(
        reverse("pledge-add", args=[item.pk]),
        {"date": "2025-09-14", "quantity": 0, "person_name": "Jane"},
        headers=HTMX,
    )
    assert response.status_code == 200
    assert response.context["form"].errors
    assert Pledge.objects.count() == 0


@pytest.mark.django_db
def test_pledge_create_invalid_without_htmx_redirects(auth_client, frozen_today, item):
    response = auth_client.post(
        reverse("pledge-add", args=[item.pk]),
        {"date": "2025-09-14", "quantity": 0, "person_name": "Jane"},
    )
    assert response.status_code == 302
    assert Pledge.objects.count() == 0


@pytest.mark.django_db
def test_pledge_create_rejects_closed_date(auth_client, frozen_today, item):
    # domingo fora do horizonte configurado ainda não tá aberto pra doações
    response = auth_client.post(
        reverse("pledge-add", args=[item.pk]),
        {"date": "2025-10-05", "quantity": 5, "person_name": "Jane"},
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_pledge_create_rejects_inactive_item(auth_client, frozen_today, item):
    item.is_active = False
    item.save(update_fields=["is_active"])
    response = auth_client.post(
        reverse("pledge-add", args=[item.pk]),
        {"date": "2025-09-14", "quantity": 5, "person_name": "Jane"},
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
        {"quantity": 25, "person_name": "John"},
    )
    assert response.status_code == 302
    pledge.refresh_from_db()
    assert pledge.quantity == 25


@pytest.mark.django_db
def test_pledge_edit_invalid_rerenders_form(auth_client, frozen_today, pledge):
    response = auth_client.post(
        reverse("pledge-edit", args=[pledge.pk]),
        {"quantity": 0, "person_name": "John"},
    )
    assert response.status_code == 200
    assert response.context["form"].errors


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
    # link do perfil na navbar, guard de nome e campo escondido de nome
    assert reverse("profile") in content
    assert "js/profile-guard.js" in content
    assert 'type="hidden" name="person_name"' in content
    assert 'placeholder="Seu nome"' not in content
