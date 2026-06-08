from django.core.management.base import BaseCommand

from donation.models import Item

ITEMS = [
    ("Água", "garrafas", 100),
    ("Biscoito", "pacotes", 20),
    ("Suco", "caixas", 30),
    ("Pão", "unidades", 200),
    ("Fruta", "unidades", 80),
]


class Command(BaseCommand):
    help = "Popula a lista de itens com itens comuns do kit de alimentação."

    def handle(self, *args, **options):
        for order, (name, unit, target) in enumerate(ITEMS):
            Item.objects.get_or_create(
                name=name,
                defaults={"unit": unit, "target_quantity": target, "order": order},
            )
        self.stdout.write(self.style.SUCCESS("Itens cadastrados."))
