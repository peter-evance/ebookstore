from time import sleep, time
from unicodedata import name
from django.test import TestCase
from django.urls import reverse
from main import factories
from main import models

from datetime import datetime
from decimal import Decimal
from unittest.mock import patch


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
        
    # def test_invoice_renders_exactly_as_expected(self):
    #     books = [
    #         factories.BookFactory(name="Book 1", active=True, price=Decimal("100.00")),
    #         factories.BookFactory(name="Book 2", active=True, price=Decimal("120.00")),
    #         ]
    #     user1 = models.User.objects.create_superuser("anonymous@gmail.com", "Abcd_123")
    #     self.client.force_login(user1)
    #     with patch("django.utils.timezone.now") as mock_time_now:
    #         mock_time_now.return_value = datetime(
    #             2022, 10, 16, 13, 59, 59)
    #         order = factories.OrderFactory(
    #             id=99,
    #             user=user1,
    #             billing_name="Peter Evance",
    #             billing_address="Odyssey gates",
    #             billing_town="Odin Halls",
    #             billing_county="Odin",
    #             )
    #     factories.OrderLineFactory.create_batch(2, order=order, book=books[0])
    #     factories.OrderLineFactory.create_batch(2, order=order, book=books[1])
    #     response = self.client.get(reverse("admin:invoice", kwargs={"order_id": order.id}))
    #     self.assertEqual(response.status_code, 200)
    #     content = response.content.decode("utf8")
    #     with open( "main/fixtures/invoice_test_order.html", "r") as fixture:
    #         expected_content = fixture.read()
    #     self.assertEqual(content, expected_content)
    #     response = self.client.get(reverse("admin:invoice", kwargs={"order_id": order.id} ),{"format": "pdf"})
    #     self.assertEqual(response.status_code, 200)
    #     content = response.content
        
    #     with open( "main/fixtures/invoice_test_order.pdf", "rb") as fixture:
    #         expected_content = fixture.read()
    #     self.assertEqual(content, expected_content)
