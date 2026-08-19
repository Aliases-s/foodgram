"""Фильтры API проекта."""
from django_filters.rest_framework import (
    AllValuesMultipleFilter,
    CharFilter,
    FilterSet,
    NumberFilter,
)

from recipes.models import Ingredient, Recipe


class IngredientFilter(FilterSet):
    """Фильтр ингредиентов по началу названия."""

    name = CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    """Фильтр рецептов по тегам, автору, избранному и покупкам."""

    tags = AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = NumberFilter(method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        """Оставляет рецепты из избранного пользователя."""
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorites__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Оставляет рецепты из списка покупок пользователя."""
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shoppingcarts__user=user)
        return queryset
