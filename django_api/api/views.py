from rest_framework import status, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.decorators import action

from .filters import RealtyFilter
from .serializers import (
    CategorySerializer,
    CitySerializer,
    CustomerSerializer,
    SearchParameterSerializer,
    RealtySerializer,
)
from .models import (
    Category,
    Customer,
    SearchParameter,
    Realty,
    City,
)


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    lookup_field = 'telegram_id'


class SearchParameterViewSet(viewsets.ModelViewSet):
    queryset = SearchParameter.objects.all()
    serializer_class = SearchParameterSerializer
    lookup_field = 'customer__telegram_id'


class RealtyViewSet(viewsets.ModelViewSet):
    queryset = Realty.objects.all()
    serializer_class = RealtySerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RealtyFilter
    pagination_class = None

    def create(self, request, *args, **kwargs):
        if isinstance(request.data, list):
            serializer = self.get_serializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )

        return super().create(request, *args, **kwargs)

    @action(
        detail=False,
        methods=['DELETE'],
        url_path='delete_all_realties',
    )
    def delete_all_realties(self, request):
        realties = Realty.objects.all()
        if not realties.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        realties.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CityReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer


class CategoryReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
