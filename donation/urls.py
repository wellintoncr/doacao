from django.urls import path

from .views import EventDetailView, PledgeCreateView, PledgeDeleteView, PledgeUpdateView

urlpatterns = [
    path("", EventDetailView.as_view(), name="event-detail"),
    path("items/<int:item_pk>/pledges/add/", PledgeCreateView.as_view(), name="pledge-add"),
    path("pledges/<int:pk>/edit/", PledgeUpdateView.as_view(), name="pledge-edit"),
    path("pledges/<int:pk>/delete/", PledgeDeleteView.as_view(), name="pledge-delete"),
]
