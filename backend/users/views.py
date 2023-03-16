from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import serializers
from .exceptions import PasswordFailedException, SubscribeException
from .mixins import ListCreateRetrieveModelMixin
from .models import Follow
from .paginations import CustomPageNumberPagination
from .utils import is_subscribed

User = get_user_model()


class UserViewSet(ListCreateRetrieveModelMixin):
    """Представление для вывода списка и создания экземпляра пользователя."""

    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = CustomPageNumberPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return serializers.UserSerializer

        return serializers.UserCreateSerializer

    @action(
        methods=['post'],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, pk):
        author = get_object_or_404(User, id=pk)

        if request.user == author:
            raise SubscribeException('Подписка на самого себя запрещена.')

        if is_subscribed(request.user, author.id):
            raise SubscribeException('Подписка уже оформлена.')

        follow = Follow.objects.create(user=request.user, author=author)
        follow.save()
        serializer = serializers.MySubscriptionsSerializer(
            author, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, pk):
        author = get_object_or_404(User, id=pk)

        if not is_subscribed(request.user, pk):
            raise SubscribeException(f'Подписка на {author} не оформлена.')

        follow = get_object_or_404(Follow, user=request.user, author=author)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        user = get_object_or_404(User, id=self.request.user.id)
        followings_id = user.follower.values_list('author_id', flat=True)
        followings = User.objects.filter(id__in=followings_id)

        page = self.paginate_queryset(followings)
        if page is not None:
            serializer = serializers.MySubscriptionsSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = serializers.MySubscriptionsSerializer(
            followings, many=True, context={'request': request}
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
            context={'request': request},
        )

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        user = get_object_or_404(User, id=request.user.id)
        serializer = serializers.UserSerializer(
            user, context={'request': request}
        )

        return Response(serializer.data)


class GetTokenView(APIView):
    """Представление для получения пользователем токена."""

    permission_classes = (AllowAny,)
    serializer_class = serializers.GetTokenSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = get_object_or_404(
            User, email=serializer.validated_data.get('email')
        )

        if user.check_password(serializer.validated_data.get('password')):
            token, _ = Token.objects.get_or_create(user=user)
            return Response(
                data={'auth_token': token.key}, status=status.HTTP_201_CREATED
            )

        raise PasswordFailedException


class SetPasswordView(APIView):
    """Представление для смены пароля."""

    serializer_class = serializers.SetPasswordViewSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(User, id=request.user.id)

        if user.check_password(
            serializer.validated_data.get('current_password')
        ):
            user.set_password(serializer.validated_data.get('new_password'))
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        raise PasswordFailedException


@api_view(['POST'])
def delete_token_view(request):
    """Представление для удаления токена пользователя."""

    token = get_object_or_404(Token, user_id=request.user.id)
    token.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)
