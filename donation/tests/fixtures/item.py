import pytest

from donation.models import Item

from .utils import random_pk


@pytest.fixture
def item(db):
    return Item.objects.create(id=random_pk(), name="Água", unit="garrafas", target_quantity=100)
