from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import (
    Category,
    City,
    Customer,
    Currency,
    Language,
    SearchParameter,
    Realty,
)


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('name',)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name',)


class CustomerSerializer(serializers.ModelSerializer):
    language = serializers.SlugRelatedField(
        slug_field='code',
        queryset=Language.objects.all(),
    )

    class Meta:
        model = Customer
        fields = '__all__'


class SearchParameterSerializer(serializers.ModelSerializer):
    customer = serializers.SlugRelatedField(
        slug_field='telegram_id',
        queryset=Customer.objects.all(),
    )
    category = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Category.objects.all(),
    )
    city = serializers.SlugRelatedField(
        slug_field='name',
        queryset=City.objects.all(),
    )

    class Meta:
        model = SearchParameter
        fields = '__all__'

    def validate(self, data):
        min_price = data.get('min_price')
        max_price = data.get('max_price')
        min_area = data.get('min_area')
        max_area = data.get('max_area')

        if min_price > max_price:
            raise ValidationError(
                'The minimum cost must be less than the maximum cost. '
                f'{min_price} > {max_price}'
            )

        if min_area > max_area:
            raise ValidationError(
                'The minimum area must be less than the maximum area. '
                f'{min_area} >  {max_area}'
            )
        return data

    def create(self, validated_data):
        customer = validated_data.pop('customer')

        search_parameters, status = SearchParameter.objects.update_or_create(
            customer=customer,
            defaults={**validated_data},
        )
        return search_parameters


class RealtySerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Category.objects.all()
    )
    city = serializers.SlugRelatedField(
        slug_field='name',
        queryset=City.objects.all()
    )
    currency = serializers.SlugRelatedField(
        slug_field='code',
        queryset=Currency.objects.all()
    )

    class Meta:
        model = Realty
        fields = '__all__'
