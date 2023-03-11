from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import FavoriteList, Ingredient, Recipe, ShoppingList, Tag
from users.paginations import CustomPageNumberPagination
from . import serializers
from .exceptions import (EmptyShoppingCart, FavoriteException,
                         ShoppingCartException)
from .filters import RecipeFilter
from .permissions import AuthorOrAdminOrReadOnly
from .utils import (get_ingredients_from_shopping_cart, is_favorited,
                    is_in_shopping_cart)


class TagViewSet(ReadOnlyModelViewSet):
    """Отображение тегов."""

    permission_classes = (AllowAny,)
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(ReadOnlyModelViewSet):
    """Отображение игредиентов."""

    serializer_class = serializers.IngredientSerializer
    permission_classes = (AllowAny,)

   def get_queryset(self):
       """
       Поиск по полю name, который ищет по началу названия,
       а так же по вхождению в произвольном месте.
       """

       search_name = self.request.query_params.get('search')

       if not search_name:
           return Ingredient.objects.all()
       qs_startswith = list(
           Ingredient.objects.filter(
               Q(name__istartswith=search_name),
           )
       )
       qs_contains = list(
           Ingredient.objects.filter(
               Q(name__icontains=search_name),
           )
       )
       queryset = [i for i in qs_contains if i not in qs_startswith]
       return qs_startswith + queryset


class RecipeViewSet(ModelViewSet):
    '''Добавление, удаление, изменение и просмотр рецептов.'''

    permission_classes = (AuthorOrAdminOrReadOnly,)
    pagination_class = CustomPageNumberPagination
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    http_method_names = [
        'get',
        'post',
        'patch',
        'delete',
        'head',
        'options',
        'trace',
    ]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return serializers.RecipeSerializer
        return serializers.CreateRecipeSerializer

    def _create(self, user, recipe, model):
        obj = model.objects.create(user=user, recipe=recipe)
        obj.save()
        serializer = serializers.ShortRecipesSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _delete(self, user, recipe, model):
        obj = get_object_or_404(model, user=user, recipe=recipe)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(method=['post'], detail=True)
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if is_favorited(request, recipe.id):
            raise FavoriteException(
                f'Рецепт {recipe} уже добавлен в избранное.'
            )
        return self._create(request.user, recipe, FavoriteList)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if not is_favorited(request, recipe.id):
            raise FavoriteException(f'Рецепт {recipe} не в избранном.')
        return self.delete(request.user, recipe, FavoriteList)

    @action(methods=['post'], detail=True)
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recupe, id=pk)
        if is_in_shopping_cart(request, recipe.id):
            raise ShoppingCartException(f'Рецепт {recipe} уже в корзине.')
        return self._create(request.user, recipe, ShoppingList)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if not is_in_shopping_cart(request, recipe.id):
            raise ShoppingCartException(f'Рецепт {recipe} не в корзине.')
        return self._delete(request.user, recipe, ShoppingList)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        name = 0
        measure = 1
        amount = 2
        ingredients = get_ingredients_from_shopping_cart(request.user)
        if not ingredients:
            raise EmptyShoppingCart
        cart = ''
        ingredients = [*ingredients]
        for i in ingredients:
            cart += f'{i[name]} ({i[measure]}) - {i[amount]} \n'
        response = HttpResponse(cart, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{file}.pdf"'
        return Response
