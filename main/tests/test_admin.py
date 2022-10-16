from time import sleep, time
from unicodedata import name
from django.test import TestCase
from django.urls import reverse
from main import factories
from main import models


class TestAdminViews(TestCase):
    def test_most_bought_books(self):
        books = [
            factories.BookFactory(name='Book 1'),
            factories.BookFactory(name='Book 2'),
            factories.BookFactory(name='Book 3'),
        ]
        user1 = models.User.objects.create_superuser(email="anonymous@gmail.com", password="Abcd_123")
        self.client.force_login(user1)
        orders = factories.OrderFactory.create_batch(3, user=user1)
        factories.OrderLineFactory.create_batch(2, order=orders[0], book=books[0])
        factories.OrderLineFactory.create_batch(2, order=orders[0], book=books[1])
        factories.OrderLineFactory.create_batch(2, order=orders[1], book=books[0])
        factories.OrderLineFactory.create_batch(2, order=orders[1], book=books[2])
        factories.OrderLineFactory.create_batch(1, order=orders[2], book=books[0])
        factories.OrderLineFactory.create_batch(1, order=orders[2], book=books[1])
    
        response = self.client.post(reverse("admin:most_bought_products"),{"period": "90"},)
        self.assertEqual(response.status_code, 200)
        data = dict(zip(
                response.context["labels"],
                response.context["values"],
                ))
        print(response.context["labels"])
        print(response.context["values"])
        self.assertEqual(data,  {"Book 2": 3, "Book 3": 2, "Book 1": 5})