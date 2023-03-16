from recipes.models import Recipe


def is_subscribed(user, author_id):
    """Проверяем подписан ли пользователь на автора."""
    return (
        user.is_authenticated
        and user.follower.filter(author_id=author_id).exists()
    )


def recipes_count(user):
    """Получаем общее число рецептов, добавленных пользователем."""
    return Recipe.objects.filter(author_id=user.id).count()


def get_limit_recipes(serializer_instance, user):
    """
    Получаем queryset модели Recipe с учетом лимита - recipes_limit,
    переданного пользователем в параметрах запроса.
    """
    request = serializer_instance.context.get('request')
    if not request:
        return user.recipes.all()

    limit = request.query_params.get('recipes_limit')
    if limit:
        return user.recipes.all()[: int(limit)]

    return user.recipes.all()
