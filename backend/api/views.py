from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.models import Subscription, User

from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (
    CreateRecipeSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    ShowSubscriptionSerializer,
    SubscriptionSerializer,
    TagSerializer,
)


class SubscribeView(APIView):
    '''Действия по подписке и отписке.'''

    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, id):
        data = {'user': request.user.id, 'author': id}
        serializer = SubscriptionSerializer(
            data=data, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        author = get_object_or_404(User, id=id)
        if Subscription.objects.filter(
            user=request.user, author=author
        ).exists():
            subscription = get_object_or_404(
                Subscription, user=request.user, author=author
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class ShowSubscriptionView(ListAPIView):
    '''Отображение подписок.'''

    permission_classes = [
        IsAuthenticated,
    ]
    pagination_class = CustomPagination

    def get(self, request):
        user = request.user
        queryset = User.objects.filter(author__user=user)
        page = self.paginate_queryset(queryset)
        serializer = ShowSubscriptionSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class FavoriteView(APIView):
    '''Добавление и удаление рецепта из избранного.'''

    permission_classes = [
        IsAuthenticated,
    ]
    pagination_class = CustomPagination

    def post(self, request, id):
        data = {'user': request.user.id, 'recipe': id}
        if not Favorite.objects.filter(
            user=request.user, recipe__id=id
        ).exists():
            serializer = FavoriteSerializer(
                data=data, context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    '''Отображение тегов.'''

    permission_classes = [
        AllowAny,
    ]
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    '''Отображение игредиентов.'''

    permission_classes = [
        AllowAny,
    ]
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = [
        IngredientFilter,
    ]
    search_field = [
        '^name',
    ]


class RecipeViewSet(viewsets.ModelViewSet):
    '''Добавление, удаление, изменение и просмотр рецептов.'''

    permission_classes = [
        IsAuthorOrAdminOrReadOnly,
    ]
    pagination_class = CustomPagination
    queryset = Recipe.objects.all()
    filter_backends = [
        DjangoFilterBackend,
    ]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return CreateRecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context


class ShoppingCartView(APIView):
    '''Добавление и удаление рецепта в корзину.'''

    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, id):
        data = {'user': request.user.id, 'recipe': id}
        recipe = get_object_or_404(Recipe, id=id)
        if not ShoppingCart.objects.filter(
            user=request.user, recipe=recipe
        ).exists():
            serializer = ShoppingCartSerializer(
                data=data, context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        if ShoppingCart.objects.filter(
            user=request.user, recipe=recipe
        ).exist():
            ShoppingCart.objects.filter(
                user=request.user, recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def download_shopping_cart(request):
    ingredients_list = 'Список покупок'
    ingredients = (
        RecipeIngredient.objrects.filter(
            recipe__shopping_cart__user=request.user
        )
        .values('ingredient__name', 'ingredient__measurement_unit')
        .annotate(amount=Sum('amount'))
    )
    for num, i in enumerate(ingredients):
        ingredients_list += (
            f"\n{i['ingredient__name']} - "
            f"{i['amount']} {i['ingredient__measurement_unit']}"
        )
        if num < ingredients.count() - 1:
            ingredients_list += ', '
    file = 'shopping_list'
    response = HttpResponse(ingredient_list, 'Content-Type: application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file}.pdf"'
    return response
