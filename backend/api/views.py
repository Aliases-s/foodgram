"""Вьюсеты API проекта."""

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import LimitPageNumberPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    AvatarSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    ShoppingCartSerializer,
    SubscriptionSerializer,
    TagSerializer,
    UserWithRecipesSerializer,
)
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.models import Subscription

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    """Вьюсет пользователей с подписками и аватаром."""

    pagination_class = LimitPageNumberPagination

    def get_permissions(self):
        """Требует авторизации для действия me."""
        if self.action == "me":
            return (IsAuthenticated(),)
        return super().get_permissions()

    @action(
        detail=False,
        methods=("put",),
        url_path="me/avatar",
        permission_classes=(IsAuthenticated,),
    )
    def avatar(self, request):
        """Обновляет аватар текущего пользователя."""
        serializer = AvatarSerializer(
            request.user,
            data=request.data,
            partial=False,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        """Удаляет аватар текущего пользователя."""
        request.user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        """Возвращает подписки текущего пользователя."""
        subscriptions = request.user.subscriptions.select_related("author")
        authors = [
            subscription.author
            for subscription in subscriptions
        ]
        page = self.paginate_queryset(authors)
        serializer = UserWithRecipesSerializer(
            page,
            many=True,
            context={"request": request},
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=("post",),
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id=None):
        """Подписывает текущего пользователя на автора."""
        get_object_or_404(User, pk=id)
        serializer = SubscriptionSerializer(
            data={"user": request.user.id, "author": id},
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        """Отписывает текущего пользователя от автора."""
        get_object_or_404(User, pk=id)
        deleted, _ = Subscription.objects.filter(
            user=request.user,
            author=id,
        ).delete()
        if not deleted:
            return Response(
                {"errors": "Подписка не найдена."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет тегов: только чтение."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет ингредиентов: только чтение и поиск по названию."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(ModelViewSet):
    """Вьюсет рецептов."""

    queryset = Recipe.objects.select_related("author").prefetch_related(
        "tags",
        "recipe_ingredients__ingredient",
    )
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ("get", "post", "patch", "delete")

    def get_serializer_class(self):
        """Выбирает сериализатор в зависимости от действия."""
        if self.action in ("list", "retrieve"):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        """Сохраняет рецепт с текущим пользователем как автором."""
        serializer.save(author=self.request.user)

    @staticmethod
    def _add_relation(serializer_class, request, pk):
        """Создаёт связь пользователя и рецепта."""
        get_object_or_404(Recipe, pk=pk)
        serializer = serializer_class(
            data={"user": request.user.id, "recipe": pk},
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def _remove_relation(model, request, pk):
        """Удаляет связь пользователя и рецепта."""
        get_object_or_404(Recipe, pk=pk)
        deleted, _ = model.objects.filter(
            user=request.user,
            recipe=pk,
        ).delete()
        if not deleted:
            return Response(
                {"errors": "Рецепт не был добавлен."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=("post",),
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        """Добавляет рецепт в избранное."""
        return self._add_relation(FavoriteSerializer, request, pk)

    @favorite.mapping.delete
    def remove_favorite(self, request, pk=None):
        """Удаляет рецепт из избранного."""
        return self._remove_relation(Favorite, request, pk)

    @action(
        detail=True,
        methods=("post",),
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        """Добавляет рецепт в список покупок."""
        return self._add_relation(ShoppingCartSerializer, request, pk)

    @shopping_cart.mapping.delete
    def remove_shopping_cart(self, request, pk=None):
        """Удаляет рецепт из списка покупок."""
        return self._remove_relation(ShoppingCart, request, pk)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        """Отдаёт файл со списком покупок."""
        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__shoppingcarts__user=request.user,
            )
            .values(
                "ingredient__name",
                "ingredient__measurement_unit",
            )
            .annotate(total=Sum("amount"))
            .order_by("ingredient__name")
        )
        lines = [
            (
                f'{item["ingredient__name"]} '
                f'({item["ingredient__measurement_unit"]}) — '
                f'{item["total"]}'
            )
            for item in ingredients
        ]
        return HttpResponse(
            "\n".join(lines),
            content_type="text/plain; charset=utf-8",
            headers={
                "Content-Disposition": (
                    'attachment; filename="shopping_list.txt"'
                ),
            },
        )

    @action(detail=True, url_path="get-link")
    def get_link(self, request, pk=None):
        """Возвращает короткую ссылку на рецепт."""
        get_object_or_404(Recipe, pk=pk)
        return Response(
            {
                "short-link": request.build_absolute_uri(
                    reverse("short-link", args=(pk,))
                ),
            }
        )
