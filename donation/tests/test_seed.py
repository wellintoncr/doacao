import pytest
from django.core.management import call_command

from donation.models import Item


@pytest.mark.django_db
def test_seed_creates_items_idempotently():
    call_command("seed")
    assert Item.objects.count() == 5
    # rodar de novo não pode duplicar a lista
    call_command("seed")
    assert Item.objects.count() == 5
