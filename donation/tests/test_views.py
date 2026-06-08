from datetime import date

import pytest
from django.urls import reverse

from donation.models import Event, Pledge

HTMX = {"HX-Request": "true"}


@pytest.mark.django_db
def test_event_detail_defaults_to_first_sunday(client, frozen_today):
    response = client.get(reverse("event-detail"))
    assert response.status_code == 200
    assert response.context["selected"] == date(2025, 9, 14)
    assert response.context["sundays"] == [date(2025, 9, 14), date(2025, 9, 21), date(2025, 9, 28)]


@pytest.mark.django_db
def test_event_detail_selects_requested_sunday(client, frozen_today):
    response = client.get(reverse("event-detail"), {"date": "2025-09-21"})
    assert response.context["selected"] == date(2025, 9, 21)


@pytest.mark.django_db
def test_event_detail_falls_back_on_invalid_date(client, frozen_today):
    response = client.get(reverse("event-detail"), {"date": "garbage"})
    assert response.context["selected"] == date(2025, 9, 14)


@pytest.mark.django_db
def test_event_detail_without_items(client, frozen_today):
    response = client.get(reverse("event-detail"))
    assert response.context["summaries"] == []


@pytest.mark.django_db
def test_event_detail_shows_pledges(client, frozen_today, pledge):
    response = client.get(reverse("event-detail"))
    summary = response.context["summaries"][0]
    assert summary["total"] == 10
    assert "John" in response.content.decode()


@pytest.mark.django_db
def test_pledge_create_creates_event_lazily(client, frozen_today, item):
    response = client.post(
        reverse("pledge-add", args=[item.pk]),
        {"date": "2025-09-21", "quantity": 40, "person_name": "Jane"},
    )
    assert response.status_code == 302
    assert response.url == f"{reverse('event-detail')}?date=2025-09-21"
    pledge = Pledge.objects.get()
    assert pledge.event.date == date(2025, 9, 21)


@pytest.mark.django_db
def test_pledge_create_reuses_existing_event(client, frozen_today, event, item):
    client.post(
        reverse("pledge-add", args=[item.pk]),
        {"date": "2025-09-14", "quantity": 5, "person_name": "Jane"},
    )
    assert Event.objects.count() == 1
    assert event.pledges.count() == 1


@pytest.mark.django_db
def test_pledge_create_htmx_returns_item_card(client, frozen_today, item):
    response = client.post(
        reverse("pledge-add", args=[item.pk]),
        {"date": "2025-09-14", "quantity": 5, "person_name": "Jane"},
        headers=HTMX,
    )
    assert response.status_code == 200
    assert "donation/partials/item_card.html" in [t.name for t in response.templates]
    assert "Jane" in response.content.decode()


@pytest.mark.django_db
def test_pledge_create_htmx_invalid_shows_errors(client, frozen_today, item):
    response = client.post(
        reverse("pledge-add", args=[item.pk]),
        {"date": "2025-09-14", "quantity": 0, "person_name": "Jane"},
        headers=HTMX,
    )
    assert response.status_code == 200
    assert response.context["form"].errors
    assert Pledge.objects.count() == 0


@pytest.mark.django_db
def test_pledge_create_invalid_without_htmx_redirects(client, frozen_today, item):
    response = client.post(
        reverse("pledge-add", args=[item.pk]),
        {"date": "2025-09-14", "quantity": 0, "person_name": "Jane"},
    )
    assert response.status_code == 302
    assert Pledge.objects.count() == 0


@pytest.mark.django_db
def test_pledge_create_rejects_closed_date(client, frozen_today, item):
    # domingo fora do horizonte configurado ainda não tá aberto pra doações
    response = client.post(
        reverse("pledge-add", args=[item.pk]),
        {"date": "2025-10-05", "quantity": 5, "person_name": "Jane"},
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_pledge_create_rejects_inactive_item(client, frozen_today, item):
    item.is_active = False
    item.save(update_fields=["is_active"])
    response = client.post(
        reverse("pledge-add", args=[item.pk]),
        {"date": "2025-09-14", "quantity": 5, "person_name": "Jane"},
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_pledge_edit_page(client, frozen_today, pledge):
    response = client.get(reverse("pledge-edit", args=[pledge.pk]))
    assert response.status_code == 200
    assert response.context["form"].instance == pledge


@pytest.mark.django_db
def test_pledge_edit_updates_pledge(client, frozen_today, pledge):
    response = client.post(
        reverse("pledge-edit", args=[pledge.pk]),
        {"quantity": 25, "person_name": "John"},
    )
    assert response.status_code == 302
    pledge.refresh_from_db()
    assert pledge.quantity == 25


@pytest.mark.django_db
def test_pledge_edit_invalid_rerenders_form(client, frozen_today, pledge):
    response = client.post(
        reverse("pledge-edit", args=[pledge.pk]),
        {"quantity": 0, "person_name": "John"},
    )
    assert response.status_code == 200
    assert response.context["form"].errors


@pytest.mark.django_db
def test_pledge_delete(client, frozen_today, pledge):
    response = client.post(reverse("pledge-delete", args=[pledge.pk]))
    assert response.status_code == 302
    assert Pledge.objects.count() == 0


@pytest.mark.django_db
def test_pledge_delete_htmx_returns_item_card(client, frozen_today, pledge):
    response = client.post(reverse("pledge-delete", args=[pledge.pk]), headers=HTMX)
    assert response.status_code == 200
    assert "donation/partials/item_card.html" in [t.name for t in response.templates]
    assert Pledge.objects.count() == 0
