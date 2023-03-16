from rest_framework.permissions import SAFE_METHODS, BasePermission


class AuthorOrAdminOrReadOnly(BasePermission):
    """
    Просмотр доступен неавторизованному пользователю.
    Добавление новых записей авторизованному пользователю.
    Редактирование записей автору или администратору.
    """

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
            or request.user.is_staff
        )
