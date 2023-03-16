from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """Пагинатор, принимающий page_size из параметров запроса."""

    page_size_query_param = 'limit'
    page_size = 6
