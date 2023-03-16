from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from .validators import validate_lowercase

User = get_user_model()


class Ingredient(models.Model):
    """Модель ингредиента"""

    name = models.CharField(max_length=200, db_index=True)
    measurement_unit = models.CharField(max_length=200)

    class Meta:
        ordering = ('name',)
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient_unit',
            )
        ]

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Тэги для рецептов."""

    name = models.CharField(
        max_length=200, unique=True, validators=(validate_lowercase,)
    )
    slug = models.SlugField(unique=True, max_length=200)
    color = ColorField(
        verbose_name='Цветовой HEX-код',
        default='#FF0000',
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} (цвет: {self.color})'


class Recipe(models.Model):
    """Модель рецепта"""

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    image = models.ImageField(upload_to='recipes/images/', max_length=300)
    text = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient'
    )
    tags = models.ManyToManyField(Tag)
    cooking_time = models.PositiveSmallIntegerField(
        validators=(
            MinValueValidator(
                1, 'Время приготовления не может быть меньше одной минуты.'
            ),
        )
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        default_related_name = 'recipes'
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Модель связи ингредиента и рецепта"""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.SmallIntegerField(
        validators=(
            MinValueValidator(
                1, 'Количество ингридиента должно быть больше единицы.'
            ),
        )
    )

    class Meta:
        default_related_name = 'recipe_ingredient'
        verbose_name = 'ингридиент к рецепту'
        verbose_name_plural = 'ингридиенты к рецепту'
        ordering = ('recipe',)
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient',
            )
        ]

    def __str__(self):
        return f'{self.recipe} -> {self.ingredient}'


class ShoppingList(models.Model):
    """Модель корзины"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        default_related_name = 'shopping'
        verbose_name = 'список покупок'
        verbose_name_plural = 'список покупок'
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping',
            )
        ]

    def __str__(self):
        return f'{self.user} -> {self.recipe}'


class FavoriteList(models.Model):
    """Модель избранного"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        default_related_name = 'favorites'
        verbose_name = 'избранное'
        verbose_name_plural = 'избранное'
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite',
            )
        ]

    def __str__(self):
        return f'{self.user} -> {self.recipe}'
