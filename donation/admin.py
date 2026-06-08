from django.contrib import admin

from .models import Event, Item, Pledge


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ["name", "unit", "target_quantity", "order", "is_active"]
    list_editable = ["target_quantity", "order", "is_active"]
    search_fields = ["name"]
    ordering = ["order", "name"]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["date"]
    ordering = ["-date"]


@admin.register(Pledge)
class PledgeAdmin(admin.ModelAdmin):
    list_display = ["person_name", "item", "quantity", "event", "created_at"]
    list_filter = ["event", "item"]
    search_fields = ["person_name"]
    ordering = ["-created_at"]
