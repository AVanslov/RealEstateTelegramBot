from rest_framework.routers import DefaultRouter
from django.urls import include, path

from .views import (
    CategoryReadOnlyViewSet,
    CityReadOnlyViewSet,
    CustomerViewSet,
    RealtyViewSet,
    SearchParameterViewSet,
)

router = DefaultRouter()
router.register('user', CustomerViewSet, basename='users')
router.register(
    'search_parameter', SearchParameterViewSet, basename='search_parameters'
)
router.register('realty', RealtyViewSet, basename='realties')
router.register('city', CityReadOnlyViewSet, basename='cities')
router.register('category', CategoryReadOnlyViewSet, basename='categories')

urlpatterns = [
    path('', include(router.urls)),
]
