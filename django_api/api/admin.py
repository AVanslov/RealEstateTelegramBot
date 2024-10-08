from django.contrib import admin
from django.db.models import Count
from django.utils.safestring import mark_safe

from .models import (
    Category,
    City,
    Customer,
    Currency,
    Language,
    SearchParameter,
    Realty,
    User,
)


class MaxPriceListFilter(admin.SimpleListFilter):
    title = ('Max price of realty')
    parameter_name = 'max_price'

    def lookups(self, request, model_admin):

        return [
            ('Expensive', ('More than 200,000 euros')),
            ('Medium', ('Less than 200,000 euros')),
            ('Cheap', ('Less than 30,000 euros')),
        ]

    def queryset(self, request, queryset):

        if self.value() == 'Cheap':
            return queryset.filter(
                max_price__range=(0, 30000),
            )
        if self.value() == 'Medium':
            return queryset.filter(
                max_price__range=(30000, 200000),
            )
        if self.value() == 'Expensive':
            return queryset.filter(
                max_price__gte=200000,
            )


class MaxAreaListFilter(admin.SimpleListFilter):
    title = ('Max area of realty')
    parameter_name = 'max_area'

    def lookups(self, request, model_admin):

        return [
            ('Huge', ('More than 100 m2')),
            ('Medium', ('Less than 100 m2')),
            ('Small', ('Less than 30 m2')),
        ]

    def queryset(self, request, queryset):

        if self.value() == 'Small':
            return queryset.filter(
                max_area__range=(0, 30),
            )
        if self.value() == 'Medium':
            return queryset.filter(
                max_area__range=(30, 100),
            )
        if self.value() == 'Huge':
            return queryset.filter(
                max_area__gte=100,
            )


class PriceListFilter(admin.SimpleListFilter):
    title = ('Price of realty')
    parameter_name = 'price'

    def lookups(self, request, model_admin):

        return [
            ('Expensive', ('More than 200,000 euros')),
            ('Medium', ('Less than 200,000 euros')),
            ('Cheap', ('Less than 30,000 euros')),
        ]

    def queryset(self, request, queryset):

        if self.value() == 'Cheap':
            return queryset.filter(
                price__range=(0, 30000),
            )
        if self.value() == 'Medium':
            return queryset.filter(
                price__range=(30000, 200000),
            )
        if self.value() == 'Expensive':
            return queryset.filter(
                price__gte=200000,
            )


class AreaListFilter(admin.SimpleListFilter):
    title = ('Area of realty')
    parameter_name = 'area'

    def lookups(self, request, model_admin):

        return [
            ('Huge', ('More than 100 m2')),
            ('Medium', ('Less than 100 m2')),
            ('Small', ('Less than 30 m2')),
        ]

    def queryset(self, request, queryset):

        if self.value() == 'Small':
            return queryset.filter(
                area__range=(0, 30),
            )
        if self.value() == 'Medium':
            return queryset.filter(
                area__range=(30, 100),
            )
        if self.value() == 'Huge':
            return queryset.filter(
                area__gte=100,
            )


class CategoryFilter(admin.SimpleListFilter):
    title = ('Category')
    parameter_name = 'category'

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        return [
            (i, "{}({})".format(j, k)) for i, j, k in
            qs.values_list('category__id', 'category__name').annotate(
                user_count=Count('category__realty', distinct=True)
            ).order_by('category__name')
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(category__id=self.value())


class CityFilter(admin.SimpleListFilter):
    title = ('City')
    parameter_name = 'city'

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        return [
            (i, "{}({})".format(j, k)) for i, j, k in
            qs.values_list('city__id', 'city__name').annotate(
                user_count=Count('city__realty', distinct=True)
            ).order_by('city__name')
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(city__id=self.value())


admin.site.register(User)

admin.site.register(Category)

admin.site.register(City)

admin.site.register(Customer)

admin.site.register(Currency)

admin.site.register(Language)


@admin.register(SearchParameter)
class SearchParameterAdmin(admin.ModelAdmin):
    list_display = (
        'customer',
        'category',
        'city',
        'min_price',
        'max_price',
        'min_area',
        'max_area',
        'rooms_number',
        'pub_date_time',
    )
    list_filter = (
        'category',
        'city',
        MaxPriceListFilter,
        MaxAreaListFilter,
        'rooms_number',
        'pub_date_time',
    )
    empty_value_display = '-empty-'
    ordering = ('-pub_date_time',)


@admin.register(Realty)
class RealtyAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'category',
        'city',
        'additional_info',
        'price',
        'area',
        'rooms_number',
        'display_image',
        'url',
        'pub_date_time',
    )
    list_filter = (
        CategoryFilter,
        CityFilter,
        AreaListFilter,
        'rooms_number',
    )
    empty_value_display = '-empty-'
    readonly_fields = ('display_image',)
    ordering = (
        'city',
        'category__name',
        'title',
        '-pub_date_time',
    )

    def display_image(self, realty):
        if realty.image_url:
            return mark_safe(
                '<img style="max-width:800px; max-height:200px;"'
                f'src="{realty.image_url}">'
            )
