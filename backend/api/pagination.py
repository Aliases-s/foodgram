"""Пагинация для API проекта."""
from rest_framework.pagination import PageNumberPagination


class LimitPageNumberPagination(PageNumberPagination):
    """Пагинация с параметром limit для размера страницы."""

    page_size_query_param = 'limit'
