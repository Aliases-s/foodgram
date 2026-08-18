"""Команда загрузки ингредиентов из JSON-файла."""
import json

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient

DATA_FILE = settings.BASE_DIR.parent / 'data' / 'ingredients.json'


class Command(BaseCommand):
    """Загружает ингредиенты из data/ingredients.json."""

    help = 'Загружает ингредиенты из data/ingredients.json'

    def handle(self, *args, **options):
        """Читает файл и создаёт ингредиенты в базе."""
        with open(DATA_FILE, encoding='utf-8') as file:
            ingredients = json.load(file)
        created = Ingredient.objects.bulk_create(
            (Ingredient(**item) for item in ingredients),
            ignore_conflicts=True,
        )
        self.stdout.write(
            self.style.SUCCESS(f'Загружено ингредиентов: {len(created)}')
        )
