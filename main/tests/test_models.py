from django.test import TestCase
from main import models
from decimal import Decimal

class TestModels(TestCase):
    def test_create_order_works(self):
        p1 = models.Book.objects.create(
            name="The cathedral and the bazaar",
            price=Decimal("10.00"),
            )
        p2 = models.Book.objects.create(
            name="Pride and Prejudice", price=Decimal("2.00"))
        user1 = models.User.objects.create_user(
            "user1", "pw432joij"
            )
        billing = models.Address.objects.create(
            user=user1,
            name="John",
            address1="127 road",
            city="Nairobi",
            county="nrb",
            )
        shipping = models.Address.objects.create(
            user=user1,
            name="John",
            address1="123 road",
            city="Nairobi",
            country="nrb",
            )
        basket = models.Basket.objects.create(user=user1)
        models.BasketLine.objects.create(
            basket=basket, product=p1
            )
        models.BasketLine.objects.create(
            basket=basket, product=p2
            )
        with self.assertLogs("main.models", level="INFO") as cm:
            order = basket.create_order(billing, shipping)
        self.assertGreaterEqual(len(cm.output), 1)
        order.refresh_from_db()
        self.assertEquals(order.user, user1)
        self.assertEquals(
            order.billing_address1, "127 road"
            )
        self.assertEquals(
            order.shipping_address1, "123 road"
            )
        # more checks to be added here
        self.assertEquals(order.lines.all().count(), 2)
        lines = order.lines.all()
        self.assertEquals(lines[0].product, p1)
        self.assertEquals(lines[1].product, p2)
