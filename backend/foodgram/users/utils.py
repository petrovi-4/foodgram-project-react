from recipes.models import Recipe


def is_subscribed(user, author_id):
    """Проверка, подписан ли пользователь на автора."""

    return (
        user.is_authenticated
        and user.follower.filter(author_id=author_id).exists()
    )


def recipe_count(user):
    """Общее количество рецептов добавленных пользователем."""

    return Recipe.objects.filter(author_id=user.id).count()


def get_limit_recipes(serializer_instance, user):
    """Список рецептов, созданных пользователем с учетом лимита"""

    request = serializer_instance.context.get('request')
    if not request:
        return user.recipe.all()
    limit = request.query_params.get('recipes_limit')
    if limit:
        return user.recipes.all()[: int(limit)]
    return user.recipes.all()
