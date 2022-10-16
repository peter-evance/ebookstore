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
        
class OrderLineFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.OrderLine

class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Order

class AddressFactory(factory.django.DjangoModelFactory): 
    class Meta:
        model = models.Address