from rest_framework.pagination import PageNumberPagination


class MaterialsPaginator(PageNumberPagination):
    """Пагинатор для вывода уроков и курсов"""

    page_size = 5