import factory
from . import models
from decimal import Decimal


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.User


class BookFactory(factory.django.DjangoModelFactory):
    price = Decimal("80")
    
    class Meta:
        model = models.Book


class AddressFactory(factory.django.DjangoModelFactory): 
    class Meta:
        model = models.Address