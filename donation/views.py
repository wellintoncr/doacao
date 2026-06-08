from django.db import transaction
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View

from .forms import PledgeForm
from .models import Event, Item, Pledge
from .utils import get_item_summaries, parse_sunday, summarize_item, upcoming_sundays


def _event_url(selected):
    return f"{reverse('event-detail')}?date={selected.isoformat()}"


def _render_item_card(request, item, selected, form=None):
    event = Event.objects.filter(date=selected).first()
    pledges = list(event.pledges.filter(item=item)) if event else []
    return render(
        request,
        "donation/partials/item_card.html",
        {
            "summary": summarize_item(item, pledges),
            "selected": selected,
            "form": form or PledgeForm(),
        },
    )


class EventDetailView(View):
    def get(self, request):
        sundays = upcoming_sundays()
        selected = parse_sunday(request.GET.get("date")) or sundays[0]
        event = Event.objects.filter(date=selected).first()
        return render(
            request,
            "donation/event_detail.html",
            {
                "sundays": sundays,
                "selected": selected,
                "summaries": get_item_summaries(event),
                "pledge_form": PledgeForm(),
            },
        )


class PledgeCreateView(View):
    def post(self, request, item_pk):
        item = get_object_or_404(Item, pk=item_pk, is_active=True)
        selected = parse_sunday(request.POST.get("date"))
        if selected is None:
            return HttpResponseBadRequest()
        form = PledgeForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                event, _ = Event.objects.get_or_create(date=selected)
                pledge = form.save(commit=False)
                pledge.event = event
                pledge.item = item
                pledge.save()
            form = None
        if request.htmx:
            return _render_item_card(request, item, selected, form=form)
        return redirect(_event_url(selected))


class PledgeUpdateView(View):
    def get(self, request, pk):
        pledge = get_object_or_404(Pledge, pk=pk)
        return self._render_form(request, pledge, PledgeForm(instance=pledge))

    def post(self, request, pk):
        pledge = get_object_or_404(Pledge, pk=pk)
        form = PledgeForm(request.POST, instance=pledge)
        if not form.is_valid():
            return self._render_form(request, pledge, form)
        form.save()
        return redirect(_event_url(pledge.event.date))

    def _render_form(self, request, pledge, form):
        return render(request, "donation/pledge_form.html", {"form": form, "pledge": pledge})


class PledgeDeleteView(View):
    def post(self, request, pk):
        pledge = get_object_or_404(Pledge, pk=pk)
        item, selected = pledge.item, pledge.event.date
        pledge.delete()
        if request.htmx:
            return _render_item_card(request, item, selected)
        return redirect(_event_url(selected))
