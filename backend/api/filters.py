"""Фильтры API проекта."""
from django_filters.rest_framework import CharFilter, FilterSet

from recipes.models import Ingredient


class IngredientFilter(FilterSet):
    """Фильтр ингредиентов по началу названия."""

    name = CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
