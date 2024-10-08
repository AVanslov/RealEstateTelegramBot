from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint

from .validators import (
    validate_found_special_symbols,
    validate_not_djoser_endpoints,
)

NAME_MAX_LENGTH = 128
EMAIL_MAX_LENGHT = 254
TITLE_MAX_LENGTH = 128
DESCRIPTION_MAX_LENGTH = 500
CURRENCY_CODE_MAX_LENGTH = 3
LANUAGE_CODE_MAX_LENGTH = 3


class User(AbstractUser):
    username = models.CharField(
        verbose_name='Username',
        max_length=NAME_MAX_LENGTH,
        unique=True,
        validators=[
            validate_found_special_symbols,
            validate_not_djoser_endpoints
        ],
    )
    email = models.EmailField(
        verbose_name='Email address',
        max_length=EMAIL_MAX_LENGHT,
        unique=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ('username',)


class Language(models.Model):
    name = models.CharField(
        'Name or language', max_length=NAME_MAX_LENGTH
    )
    code = models.CharField(
        'Language code', max_length=LANUAGE_CODE_MAX_LENGTH
    )

    def __str__(self) -> str:
        return self.code

    class Meta:
        ordering = ('code',)


class Customer(models.Model):
    telegram_id = models.PositiveBigIntegerField(
        'Telegram id', unique=True, help_text='Telegram id'
    )
    username = models.CharField(
        'Username', max_length=NAME_MAX_LENGTH, unique=True,
        help_text='Telegram username'
    )
    language = models.ForeignKey(
        Language, null=True, on_delete=models.SET_NULL
    )

    def __str__(self) -> str:
        return f'telegram id: {self.telegram_id}, username: {self.username}'

    class Meta:
        ordering = ('username',)


class City(models.Model):
    name = models.CharField(
        'City name', max_length=NAME_MAX_LENGTH, unique=True
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ('name',)


class Category(models.Model):
    name = models.CharField(
        'Realty category name',
        max_length=NAME_MAX_LENGTH,
        unique=True,
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ('name',)


class SearchParameter(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    min_price = models.PositiveIntegerField('Min price in euro')
    max_price = models.PositiveIntegerField('Max price in euro')
    min_area = models.PositiveIntegerField('Min area in m2')
    max_area = models.PositiveIntegerField('Max area in m2')
    rooms_number = models.FloatField('Number of rooms')
    pub_date_time = models.DateTimeField(
        'Date and time',
        auto_now=True,
        help_text='Date and time of the last search query'
    )

    def __str__(self) -> str:
        return (
            f'{self.customer.telegram_id}-{self.city.name}'
        )

    class Meta:
        ordering = ('-pub_date_time', 'city__name', 'category__name')


class Currency(models.Model):
    name = models.CharField(
        'Currency full name',
        max_length=NAME_MAX_LENGTH,
        blank=True,
        unique=True
    )
    code = models.CharField(
        'ISO currency code',
        max_length=CURRENCY_CODE_MAX_LENGTH,
        unique=True
    )

    def __str__(self):
        return (
            f' {self.code}'
        )

    class Meta:
        ordering = ('code',)


class Realty(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    additional_info = models.CharField(
        'Additional address',
        max_length=DESCRIPTION_MAX_LENGTH,
        blank=True,
        null=True,
        help_text='Additional information about address'
    )
    title = models.CharField(
        'Title', null=True, blank=True, max_length=TITLE_MAX_LENGTH
    )
    description = models.TextField(
        'Description', null=True, blank=True, max_length=DESCRIPTION_MAX_LENGTH
    )
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    price = models.PositiveIntegerField('Price', null=True, blank=True)
    area = models.PositiveIntegerField('Area', null=True, blank=True)
    rooms_number = models.FloatField('Number of rooms', null=True, blank=True)
    image_url = models.URLField(
        'Link to the main image',
        blank=True,
        null=False,
        unique=True,
    )
    url = models.URLField(
        'Link to the real estate',
        blank=False,
        null=False,
        unique=True
    )
    pub_date_time = models.DateTimeField(
        'Ad download date and time',
        auto_now_add=True,
        auto_now=False,
    )

    def __str__(self):
        if self.title:
            return (
                f'{self.title}-{self.city}-{self.category}'
            )
        else:
            return (
                f'{self.city}-{self.category}'
            )

    class Meta:
        ordering = ('-pub_date_time',)
        constraints = [
            UniqueConstraint(
                fields=['city', 'category', 'url'],
                name='unique_city_category_url_realty'
            ),
        ]
