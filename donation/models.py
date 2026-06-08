from django.core.validators import MinValueValidator
from django.db import models


class Item(models.Model):
    """Um item que o grupo precisa todo domingo. A lista é gerenciada pelo admin."""

    name = models.CharField("nome", max_length=100, unique=True)
    unit = models.CharField(
        "unidade",
        max_length=30,
        help_text="Exibido após as quantidades, ex.: garrafas, pacotes.",
    )
    target_quantity = models.PositiveIntegerField("quantidade desejada", validators=[MinValueValidator(1)])
    order = models.PositiveIntegerField("ordem", default=0)
    is_active = models.BooleanField("ativo", default=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "item"
        verbose_name_plural = "itens"

    def __str__(self):
        return self.name


class Event(models.Model):
    """Um domingo de doação. Criado sob demanda quando chega a primeira doação pra data."""

    date = models.DateField("data", unique=True)

    class Meta:
        ordering = ["date"]
        verbose_name = "evento"
        verbose_name_plural = "eventos"

    def __str__(self):
        return self.date.isoformat()


class Pledge(models.Model):
    """O compromisso de um voluntário: levar tal quantidade de um item num domingo."""

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="pledges", verbose_name="evento")
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name="pledges", verbose_name="item")
    person_name = models.CharField("nome", max_length=60)
    quantity = models.PositiveIntegerField("quantidade", validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "doação"
        verbose_name_plural = "doações"

    def __str__(self):
        return f"{self.person_name} ({self.quantity})"
