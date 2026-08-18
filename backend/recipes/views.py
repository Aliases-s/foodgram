"""Вьюхи приложения recipes."""
from django.shortcuts import get_object_or_404, redirect

from recipes.models import Recipe


def short_link_redirect(request, pk):
    """Перенаправляет короткую ссылку на страницу рецепта."""
    get_object_or_404(Recipe, pk=pk)
    return redirect(f'/recipes/{pk}/')
