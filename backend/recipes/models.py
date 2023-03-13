from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import UniqueConstraint

User = get_user_model()


class Ingredient(models.Model):
    """Модель ингредиента"""

    name = models.CharField(
        'Название ингредиента', max_length=200, db_index=True
    )
    measurement_unit = models.CharField('Единица измерения', max_length=200)

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='ingredient_name_unit_unique',
            )
        ]


class Tag(models.Model):
    """Тэги для рецептов."""

    name = models.CharField(
        verbose_name='Тэг',
        max_length=200,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='Слаг тэга', unique=True, max_length=200
    )
    color = ColorField(
        verbose_name='Цветовой HEX-код',
        default='#FF0000',
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)

    def __str__(self) -> str:
        return f'{self.name} (цвет: {self.color})'


class Recipe(models.Model):
    """Модель рецепта"""

    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        verbose_name='Тэги',
        related_name='tags',
        db_index=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name='recipes',
        db_index=True,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
        db_index=True,
    )
    image = models.ImageField('Изображение', upload_to='recipes/images/')
    name = models.CharField('Название рецепта', max_length=200, db_index=True)
    text = models.TextField(
        'Описание рецепта', help_text='Введите описание рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(
                1, message='Время приготовления не может быть менее 1 минуты!'
            )
        ],
    )
    pub_date = models.DateTimeField(
        'Время публикации',
        auto_now_add=True,
    )

    class Meta:
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
        'Количество', validators=[MinValueValidator(1)]
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='recipe_ingredient_unique',
            )
        ]


class RecipeTag(models.Model):
    """Модель связи тэга и рецепта"""

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт'
    )
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, verbose_name='Тэг')

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['recipe', 'tag'], name='recipe_tag_unique'
            )
        ]


class ShoppingCart(models.Model):
    """Модель корзины"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_cart',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shopping_cart',
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'], name='user_shoppingcart_unique'
            )
        ]


class Favorite(models.Model):
    """Модель избранного"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorites',
        db_index=True,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='favorites',
        db_index=True,
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'], name='user_favorite_unique'
            )
        ]
