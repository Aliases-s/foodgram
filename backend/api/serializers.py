"""Сериализаторы API проекта."""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.fields import Base64ImageField
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

MIN_INGREDIENT_AMOUNT = 1
MIN_COOKING_TIME = 1


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "avatar",
        )

    def get_is_subscribed(self, obj):
        """Определяет, подписан ли текущий пользователь на этого."""
        user = self.context["request"].user
        return (
            user.is_authenticated
            and Subscription.objects.filter(user=user, author=obj).exists()
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тега."""

    class Meta:
        model = Tag
        fields = ("id", "name", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента."""

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента внутри рецепта при чтении."""

    id = serializers.IntegerField(source="ingredient.id")
    name = serializers.CharField(source="ingredient.name")
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта для чтения."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        many=True,
        read_only=True,
        source="recipe_ingredients",
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, obj):
        """Определяет, находится ли рецепт в избранном."""
        user = self.context["request"].user
        return (
            user.is_authenticated
            and obj.favorites.filter(user=user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        """Определяет, находится ли рецепт в списке покупок."""
        user = self.context["request"].user
        return (
            user.is_authenticated
            and obj.shoppingcarts.filter(user=user).exists()
        )


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента внутри рецепта при записи."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ("id", "amount")


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта для создания и обновления."""

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    ingredients = RecipeIngredientWriteSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
        )

    def validate(self, data):
        """Проверяет наличие и уникальность тегов и ингредиентов."""
        tags = data.get("tags")
        if not tags:
            raise serializers.ValidationError(
                {"tags": "Нужен хотя бы один тег."}
            )
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                {"tags": "Теги не должны повторяться."}
            )
        ingredients = data.get("ingredients")
        if not ingredients:
            raise serializers.ValidationError(
                {"ingredients": "Нужен хотя бы один ингредиент."}
            )
        ingredient_ids = [item["id"] for item in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                {"ingredients": "Ингредиенты не должны повторяться."}
            )
        return data

    @staticmethod
    def _set_ingredients(recipe, ingredients):
        """Записывает ингредиенты рецепта."""
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=item["id"],
                amount=item["amount"],
            )
            for item in ingredients
        )

    def create(self, validated_data):
        """Создаёт рецепт с тегами и ингредиентами."""
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self._set_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        """Обновляет рецепт с тегами и ингредиентами."""
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        instance.tags.set(tags)
        instance.recipe_ingredients.all().delete()
        self._set_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Возвращает рецепт в формате сериализатора чтения."""
        return RecipeReadSerializer(instance, context=self.context).data


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта в сокращённой форме."""

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class UserRecipeRelationSerializer(serializers.ModelSerializer):
    """Базовый сериализатор связи пользователя и рецепта."""

    class Meta:
        fields = ("user", "recipe")

    def validate(self, data):
        """Проверяет, что рецепт ещё не добавлен."""
        if self.Meta.model.objects.filter(**data).exists():
            raise serializers.ValidationError("Рецепт уже добавлен.")
        return data

    def to_representation(self, instance):
        """Возвращает рецепт в сокращённой форме."""
        return RecipeMinifiedSerializer(
            instance.recipe, context=self.context
        ).data


class FavoriteSerializer(UserRecipeRelationSerializer):
    """Сериализатор избранного."""

    class Meta(UserRecipeRelationSerializer.Meta):
        model = Favorite


class ShoppingCartSerializer(UserRecipeRelationSerializer):
    """Сериализатор списка покупок."""

    class Meta(UserRecipeRelationSerializer.Meta):
        model = ShoppingCart


class UserWithRecipesSerializer(UserSerializer):
    """Сериализатор пользователя с рецептами для подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source="recipes.count",
        read_only=True,
    )

    class Meta(UserSerializer.Meta):
        fields = (*UserSerializer.Meta.fields, "recipes", "recipes_count")

    def get_recipes(self, obj):
        """Возвращает рецепты автора с учётом recipes_limit."""
        recipes = obj.recipes.all()
        limit = self.context["request"].query_params.get("recipes_limit")
        if limit and limit.isdigit():
            recipes = recipes[: int(limit)]
        return RecipeMinifiedSerializer(
            recipes, many=True, context=self.context
        ).data


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор создания подписки."""

    class Meta:
        model = Subscription
        fields = ("user", "author")

    def validate(self, data):
        """Проверяет подписку на себя и повторную подписку."""
        if data["user"] == data["author"]:
            raise serializers.ValidationError(
                "Нельзя подписаться на самого себя."
            )
        if Subscription.objects.filter(**data).exists():
            raise serializers.ValidationError("Подписка уже существует.")
        return data

    def to_representation(self, instance):
        """Возвращает автора с рецептами."""
        return UserWithRecipesSerializer(
            instance.author, context=self.context
        ).data


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор аватара пользователя."""

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ("avatar",)
