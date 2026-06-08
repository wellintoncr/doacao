import pytest


@pytest.mark.django_db
def test_item_str(item):
    assert str(item) == "Água"


@pytest.mark.django_db
def test_event_str(event):
    assert str(event) == "2025-09-14"


@pytest.mark.django_db
def test_pledge_str(pledge):
    assert str(pledge) == "John (10)"
