from rest_framework_json_api.pagination import PageNumberPagination


class NossPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
