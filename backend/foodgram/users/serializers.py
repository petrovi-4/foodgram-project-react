from django.contrib.auth import get_user_model
from rest_framework import serializers

from recipes.models import Recipe
from .utils import get_limit_recipes, is_subscribed, recipe_count

User = get_user_model()
IS_SUBSCRIBE_KEY = 'is_subscribed'


class GetToketSerializer(serializers.Serializer):
    """Сериалиалайзер для получения токена пользователем."""

    email = serializers.EmailField(required=True, write_only=True)
    password = serializers.CharField(
        max_length=150, required=True, write_only=True
    )


class UserSerializer(serializers.ModelSerializer):
    """Сериалайзер списка пользователей."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            IS_SUBSCRIBE_KEY,
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request:
            return False
        return is_subscribed(request.user, obj.id)


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        read_only_fields = ('id',)
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class SetPasswordViewSerializer(serializers.Serializer):
    """Сериалайзер для смены пароля."""

    new_password = serializers.CharField(
        max_length=150, required=True, write_only=True
    )
    current_password = serializers.CharField(
        max_length=150, required=True, write_only=True
    )


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для короткого отображения рецепта."""

    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )

    def get_image(self, obj):
        request = self.context.get('request')
        photo_url = obj.image.url
        return request.build_absolute_uri(photo_url)


class MySubscriptionSerializer(UserSerializer):
    """Сериалайзер для просмотра своих подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            IS_SUBSCRIBE_KEY,
            'recipes',
            'recipe_count',
        )

    def get_recipes_count(self, obj):
        return recipe_count(obj)

    def get_recipes(self, obj):
        queryset = get_limit_recipes(self, obj)
        return ShortRecipeSerializer(
            queryset,
            many=True,
            context={'request': self.context.get('request')},
        ).data
