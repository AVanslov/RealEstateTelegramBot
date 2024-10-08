import django_filters

from .models import Realty


class RealtyFilter(django_filters.FilterSet):

    class Meta:
        model = Realty
        fields = {
            'category__name': ['exact'],
            'city__name': ['exact'],
            'price': ['lt', 'gt'],
            'area': ['lt', 'gt'],
        }
