from recipes.models import RecipeIngredient


def is_favorited(request, recipe_id):
    """Проверяем, добавлен ли рецепт в избранное."""

    if not request:
        return False
    return (
        request.user.is_authenticated
        and request.user.favorites.filter(recipe_id=recipe_id).exists()
    )


def is_in_shopping_cart(request, recipe_id):
    """Проверяем, добавлен ли рецепт в корзину."""

    if not request:
        return False
    return (
        request.user.is_authenticated
        and request.user.shopping.filter(recipe_id=recipe_id).exists()
    )


def get_ingredients_from_shopping_cart(user):
    recipes_id = user.shopping.values_list('recipe_id', flat=True)
    recipes_ingredients = RecipeIngredient.objects.filter(
        recipe_id__in=recipes_id
    )
    amount_index = 2
    ingredients = {}
    for i in recipes_ingredients:
        if ingredients.get(i.ingredient) is None:
            ingredients[i.ingredient] = i.amount
            ingredients[i.ingredient] = [
                i.ingredient.name,
                i.ingredient.measurement_unit,
                i.amount,
            ]
        else:
            ingredients[i.ingredient][amount_index] += i.amount
    return ingredients.values()
