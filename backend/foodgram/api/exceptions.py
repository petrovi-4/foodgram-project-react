from rest_framework import status
from rest_framework.exceptions import APIException


class FavoriteException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST


class ShoppingCartException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST


class EmptyShoppingCart(APIException):
    status_code = status.HTTP_204_NO_CONTENT
    default_detail = 'Корзина пуста.'
