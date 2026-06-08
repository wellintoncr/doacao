from datetime import date

import pytest

from donation.models import Event

from .utils import random_pk


@pytest.fixture
def event(db):
    return Event.objects.create(id=random_pk(), date=date(2025, 9, 14))
