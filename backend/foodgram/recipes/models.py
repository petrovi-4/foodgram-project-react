from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from django.db import models

from .validators import validate_lowercase

User = get_user_model()


class Ingredient(models.Model):
    """Модель ингредиента"""

    name = models.CharField(
        'Название ингредиента', max_length=200, db_index=True
    )
    measurement_unit = models.CharField('Единица измерения', max_length=200)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient_unit',
            )
        ]


class Tag(models.Model):
    """Модель тэга"""

    name = models.CharField(
        'Название тэга',
        max_length=200,
        db_index=True,
        validators=(validate_lowercase,),
    )
    color = models.CharField('Цвет', unique=True, max_length=7)
    slug = models.SlugField('Slug', unique=True, max_length=200)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта"""

    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
        related_name='tags',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
    )
    image = models.ImageField('Изображение', upload_to='recipes/images/')
    name = models.CharField('Название рецепта', max_length=200, db_index=True)
    text = models.TextField(
        'Описание рецепта', help_text='Введите описание рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=(
            MinValueValidator(
                1, message='Время приготовления не может быть менее 1 минуты!'
            ),
        ),
    )
    pub_date = models.DateTimeField(
        'Время публикации',
        auto_now_add=True,
    )

    class Meta:
        default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Модель связи ингредиента и рецепта"""

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=(
            MinValueValidator(
                1, 'Количество ингредиента должно быть больше единицы.'
            ),
        ),
    )

    class Meta:
        default_related_name = 'recipe_ingredient'
        verbose_name = 'Ингредиент к рецепту'
        verbose_name_plural = 'Ингредиенты к рецепту'
        ordering = ('recipe',)
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient',
            )
        ]

        def __str__(self):
            return f'{self.recipe} -> {self.ingredient}'


class FavoriteList(models.Model):
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


class ShoppingList(models.Model):
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
