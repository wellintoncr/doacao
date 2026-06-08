from datetime import date

import pytest

from .fixtures.event import *  # noqa: F401, F403
from .fixtures.item import *  # noqa: F401, F403
from .fixtures.pledge import *  # noqa: F401, F403


@pytest.fixture
def frozen_today(monkeypatch):
    """Congela o "hoje" na quarta 2025-09-10; os próximos domingos viram 14, 21 e 28/09."""
    monkeypatch.setattr("django.utils.timezone.localdate", lambda: date(2025, 9, 10))
