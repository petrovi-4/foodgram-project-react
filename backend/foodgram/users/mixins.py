from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet


class ListCreateRetrieveModelMixin(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    pass
