from collections import defaultdict
from datetime import date, timedelta

from django.conf import settings
from django.utils import timezone

from .models import Item


def upcoming_sundays():
    """Os domingos abertos pra doação, contando hoje se hoje já for domingo."""
    today = timezone.localdate()
    first = today + timedelta(days=(6 - today.weekday()) % 7)
    return [first + timedelta(weeks=week) for week in range(settings.UPCOMING_SUNDAYS_COUNT)]


def parse_sunday(value):
    """Devolve o valor como data se for um dos próximos domingos, senão None."""
    try:
        parsed = date.fromisoformat(value or "")
    except ValueError:
        return None
    return parsed if parsed in upcoming_sundays() else None


def summarize_item(item, pledges):
    total = sum(pledge.quantity for pledge in pledges)
    target = item.target_quantity
    return {
        "item": item,
        "pledges": pledges,
        "total": total,
        "remaining": max(target - total, 0),
        "is_satisfied": total >= target,
        "percent": min(100, round(total * 100 / target)) if target else 100,
    }


def get_item_summaries(event):
    """Totais de doação por item de um evento; o evento pode nem existir ainda (sem doações)."""
    pledges_by_item = defaultdict(list)
    if event is not None:
        for pledge in event.pledges.select_related("user"):
            pledges_by_item[pledge.item_id].append(pledge)
    items = Item.objects.filter(is_active=True)
    return [summarize_item(item, pledges_by_item[item.pk]) for item in items]
