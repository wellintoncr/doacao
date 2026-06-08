import pytest

from donation.models import Pledge

from .utils import random_pk


@pytest.fixture
def pledge(db, event, item):
    return Pledge.objects.create(
        id=random_pk(),
        event=event,
        item=item,
        person_name="John",
        quantity=10,
    )
