from django.test import TestCase
from main import models
from decimal import Decimal

class TestModels(TestCase):
    
    def test_book_manager_works(self):
        models.Book.objects.create(
            name="Laws of human nature", price=Decimal("30.00"))
        self.assertEqual(len(models.Book.objects.active()), 1)
    
    def test_create_order_works(self):
        bk1 = models.Book.objects.create(
            name="The cathedral and the bazaar",
            price=Decimal("10.00"))
        bk2 = models.Book.objects.create(
            name="Pride and Prejudice",
            price=Decimal("2.00"))
        user1 = models.User.objects.create_user("anonymous@gmail.com", "Abcd_123")
        billing = models.Address.objects.create(
            user=user1,
            name="Peter",
            address="State House",
            town="Nairobi",
            county="nrb")
        shipping = models.Address.objects.create(
            user=user1,
            name="Anonymous",
            address="4 Chan",
            town="Kisumu",
            county="nrb")
        basket = models.Basket.objects.create(user=user1)
        models.BasketLine.objects.create(basket=basket, book=bk1)
        models.BasketLine.objects.create(basket=basket, book=bk2)
        with self.assertLogs("main.models", level="INFO") as cm:
            order = basket.create_order(billing, shipping)
        self.assertGreaterEqual(len(cm.output), 1)
        order.refresh_from_db()
        self.assertEquals(order.user, user1)
        self.assertEquals(order.billing_address, "State House")
        self.assertEquals(order.shipping_address, "4 Chan")
        self.assertEquals(order.lines.all().count(), 2)
        lines = order.lines.all()
        self.assertEquals(lines[0].book, bk1)
        self.assertEquals(lines[1].book, bk2)
