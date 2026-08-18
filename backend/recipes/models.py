"""Модели приложения recipes."""
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()

MAX_TAG_LENGTH = 32
MAX_INGREDIENT_NAME_LENGTH = 128
MAX_MEASUREMENT_UNIT_LENGTH = 64
MAX_RECIPE_NAME_LENGTH = 256
MIN_COOKING_TIME = 1
MIN_INGREDIENT_AMOUNT = 1


class Tag(models.Model):
    """Тег рецепта."""

    name = models.CharField(
        'Название',
        max_length=MAX_TAG_LENGTH,
        unique=True,
    )
    slug = models.SlugField(
        'Слаг',
        max_length=MAX_TAG_LENGTH,
        unique=True,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        """Возвращает название тега."""
        return self.name


class Ingredient(models.Model):
    """Ингредиент."""

    name = models.CharField(
        'Название',
        max_length=MAX_INGREDIENT_NAME_LENGTH,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=MAX_MEASUREMENT_UNIT_LENGTH,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient_name_unit',
            ),
        )

    def __str__(self):
        """Возвращает название ингредиента."""
        return self.name


class Recipe(models.Model):
    """Рецепт."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    name = models.CharField(
        'Название',
        max_length=MAX_RECIPE_NAME_LENGTH,
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/images/',
    )
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления (мин)',
        validators=(MinValueValidator(MIN_COOKING_TIME),),
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        """Возвращает название рецепта."""
        return self.name


class RecipeIngredient(models.Model):
    """Ингредиент в рецепте с указанием количества."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=(MinValueValidator(MIN_INGREDIENT_AMOUNT),),
    )

    class Meta:
        verbose_name = 'ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient',
            ),
        )

    def __str__(self):
        """Возвращает связку рецепта и ингредиента."""
        return f'{self.recipe}: {self.ingredient}'


class UserRecipeRelation(models.Model):
    """Абстрактная связь пользователя и рецепта."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)ss',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='%(class)ss',
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='%(app_label)s_%(class)s_unique',
            ),
        )

    def __str__(self):
        """Возвращает связку пользователя и рецепта."""
        return f'{self.user}: {self.recipe}'


class Favorite(UserRecipeRelation):
    """Избранный рецепт пользователя."""

    class Meta(UserRecipeRelation.Meta):
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(UserRecipeRelation):
    """Рецепт в списке покупок пользователя."""

    class Meta(UserRecipeRelation.Meta):
        verbose_name = 'список покупок'
        verbose_name_plural = 'Списки покупок'
