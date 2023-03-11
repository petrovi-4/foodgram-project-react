import io
from reportlab.pdfgen import canvas
from urllib.parse import unquote

from django.contrib.auth import get_user_model
from django.http.response import HttpResponse
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_401_UNAUTHORIZED
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import Ingredient, IngredientQuantity, Recipe, Tag

from .mixins import AddDelViewMixin
from .pagination import PageLimitPagination
from .permissions import IsAdminOrReadOnly, IsAuthorStaffOrReadOnly
from .serializers import (
    IngredientSerializer,
    RecipeSerializer,
    ShortRecipeSerializer,
    TagSerializer,
    UserSubscribeSerializer,
)

User = get_user_model()


class UserViewSet(DjoserUserViewSet, AddDelViewMixin):
    """ViewSet для работы с пользователями."""

    pagination_class = PageLimitPagination
    add_serializer = UserSubscribeSerializer

    @action(
        methods=(
            'GET',
            'POST',
            'DELETE',
        ),
        detail=True,
    )
    def subscribe(self, request, id):
        return self.add_remove_relation(id, 'follow_M2M')

    @action(methods=('get',), detail=False)
    def subscriptions(self, request):
        user = self.request.user
        if user.is_anonymous:
            return Response(status=HTTP_401_UNAUTHORIZED)
        authors = user.follow.all()
        pages = self.paginate_queryset(authors)
        serializer = UserSubscribeSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(ReadOnlyModelViewSet):
    """ViewSet для работы с тэгами."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(ReadOnlyModelViewSet):
    """ViewSet для работы с игридиентами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def get_queryset(self):
        """Ищет объекты по совпадению в начале названия,
        также добавляются результаты по совпадению в середине.
        Прописные буквы преобразуются в строчные,
        """
        name = self.request.query_params.get('name')
        queryset = self.queryset
        if name:
            if name[0] == '%':
                name = unquote(name)
            name = name.lower()
            stw_queryset = list(queryset.filter(name__startswith=name))
            cnt_queryset = queryset.filter(name__contains=name)
            stw_queryset.extend(
                [i for i in cnt_queryset if i not in stw_queryset]
            )
            queryset = stw_queryset
        return queryset


class RecipeViewSet(ModelViewSet, AddDelViewMixin):
    """ViewSet для работы  с рецептами."""

    queryset = Recipe.objects.select_related('author')
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorStaffOrReadOnly,)
    pagination_class = PageLimitPagination
    add_serializer = ShortRecipeSerializer

    def get_queryset(self):
        """Фильтрация в соответствии с параметрами запроса."""
        queryset = self.queryset

        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author=author)

        user = self.request.user
        if user.is_anonymous:
            return queryset

        is_in_shopping = self.request.query_params.get('is_in_shopping_cart')
        if is_in_shopping in (
            '1',
            'true',
        ):
            queryset = queryset.filter(is_in_shopping_list=user.id)
        elif is_in_shopping in (
            '0',
            'false',
        ):
            queryset = queryset.exclude(is_in_shopping_list=user.id)

        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited in (
            '1',
            'true',
        ):
            queryset = queryset.filter(is_favorite=user.id)
        if is_favorited in (
            '0',
            'false',
        ):
            queryset = queryset.exclude(is_favorite=user.id)

        return queryset

    @action(
        methods=(
            'GET',
            'POST',
            'DELETE',
        ),
        detail=True,
    )
    def favorite(self, request, pk):
        """Добавляет/удалет рецепт в `избранное`."""
        return self.add_remove_relation(pk, 'is_favorite_M2M')

    @action(
        methods=(
            'GET',
            'POST',
            'DELETE',
        ),
        detail=True,
    )
    def shopping_cart(self, request, pk):
        """Добавляет/удалет рецепт в `список покупок`."""
        return self.add_remove_relation(pk, 'shopping_cart_M2M')

    @api_view(['GET'])
    def download_shopping_list(request):
        user = request.user
        if user.is_anonymous:
            return Response(status=HTTP_401_UNAUTHORIZED)

        recipes = Recipe.objects.filter(
            is_in_shopping_list=user
        ).select_related('author')
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer)
        pdf.setFont('Helvetica-Bold', 14)
        pdf.drawString(50, 750, 'Список покупок')
        pdf.setFont('Helvetica', 12)
        y = 700
        for recipe in recipes:
            pdf.drawString(50, y, f'{recipe.title} ({recipe.author.username})')
            y -= 20
            for ingredient in recipe.ingredients.all():
                pdf.drawString(
                    70,
                    y,
                    f'{ingredient.name} - {ingredient.amount} {ingredient.unit_of_measurement}',
                )
                y -= 20
            y -= 10
        pdf.showPage()
        pdf.save()
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response[
            'Content-Disposition'
        ] = 'attachment; filename="shopping_list.pdf"'
        return response
