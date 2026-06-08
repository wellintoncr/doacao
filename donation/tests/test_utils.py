from datetime import date

import pytest

from donation.models import Item
from donation.utils import get_item_summaries, parse_sunday, summarize_item, upcoming_sundays


def test_upcoming_sundays_midweek(frozen_today):
    assert upcoming_sundays() == [date(2025, 9, 14), date(2025, 9, 21), date(2025, 9, 28)]


def test_upcoming_sundays_starts_today_on_sunday(monkeypatch):
    monkeypatch.setattr("django.utils.timezone.localdate", lambda: date(2025, 9, 14))
    assert upcoming_sundays()[0] == date(2025, 9, 14)


def test_upcoming_sundays_count_from_settings(frozen_today, settings):
    settings.UPCOMING_SUNDAYS_COUNT = 1
    assert upcoming_sundays() == [date(2025, 9, 14)]


def test_parse_sunday_accepts_upcoming_sunday(frozen_today):
    assert parse_sunday("2025-09-21") == date(2025, 9, 21)


def test_parse_sunday_rejects_missing_garbage_and_other_dates(frozen_today):
    assert parse_sunday(None) is None
    assert parse_sunday("not-a-date") is None
    # data ISO válida mas que não é um domingo aberto não pode receber doação
    assert parse_sunday("2025-09-15") is None
    assert parse_sunday("2025-10-05") is None


def test_summarize_item_totals_and_flags(item):
    summary = summarize_item(item, [])
    assert summary["total"] == 0
    assert summary["remaining"] == 100
    assert summary["is_satisfied"] is False
    assert summary["percent"] == 0


def test_summarize_item_overpledged_caps_percent_and_floors_remaining(pledge):
    pledge.quantity = 150
    summary = summarize_item(pledge.item, [pledge])
    assert summary["remaining"] == 0
    assert summary["is_satisfied"] is True
    assert summary["percent"] == 100


def test_summarize_item_zero_target_treated_as_satisfied():
    item = Item(name="x", unit="u", target_quantity=0)
    summary = summarize_item(item, [])
    assert summary["percent"] == 100
    assert summary["is_satisfied"] is True


@pytest.mark.django_db
def test_get_item_summaries_without_event(item):
    summaries = get_item_summaries(None)
    assert len(summaries) == 1
    assert summaries[0]["pledges"] == []


@pytest.mark.django_db
def test_get_item_summaries_skips_inactive_items(item, pledge):
    item.is_active = False
    item.save(update_fields=["is_active"])
    assert get_item_summaries(pledge.event) == []
