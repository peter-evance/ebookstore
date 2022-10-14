from main import forms, models
from django.test import TestCase
from django.urls import reverse
from decimal import Decimal
from unittest.mock import patch
from django.contrib import auth


class TestPage(TestCase):
    '''Test for http status code = 200 OK, if respective html template is used and
    response containing name ebookstore.
    '''

    def test_home_page_works(self):
        # response = self.client.get(reverse("home"))
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, 'ebookstore')

    def test_about_us_works(self):
        response = self.client.get(reverse("about-us"))
        # response = self.client.get('/about_us/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about_us.html')
        self.assertContains(response, 'ebookstore')

    def test_contact_us_page_works(self):
        response = self.client.get(reverse('contact_us'))
        # response = self.client.get('/contact_us/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact_us.html')
        self.assertContains(response, 'ebookstore')
        self.assertIsInstance(response.context['form'], forms.ContactUsForm)

    def test_books_page_returns_active(self):
        models.Book.objects.create(
            name="The cathedral and the bazaar",
            slug="cathedral-bazaar",
            price=Decimal("10.00"),)
        models.Book.objects.create(
            name="A Tale of Two Cities",
            slug="tale-two-cities",
            price=Decimal("2.00"),
            active=False,)
        response = self.client.get(
            reverse("books", kwargs={"tag": "all"}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ebookstore")
        book_list = models.Book.objects.active().order_by("name")
        self.assertEqual(list(response.context["object_list"]), list(book_list))

    def test_products_page_filters_by_tags_and_active(self):
        cp = models.Book.objects.create(
            name="The Laws of Human Nature",
            slug="the-laws-of-human-nature",
            price=Decimal("100.0"))
        cp.tags.create(name="Personal development", slug="personal-development")
        response = self.client.get(reverse("books", kwargs={"tag": "personal-development"}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ebookstore")
        book_list = models.Book.objects.active().filter(tags__slug="personal-development")
        self.assertEqual(list(response.context["object_list"]), list(book_list))

    def test_user_signup_page_loads_correctly(self):
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "signup.html")
        self.assertContains(response, "ebookstore")
        self.assertIsInstance(response.context["form"], forms.UserCreationForm)
    
    def test_user_signup_page_submission_works(self):
        post_data = {
            "email": "testpeterevance1@gmail.com",
            "password1": "Abcd_123",
            "password2": "Abcd_123",
            }
        with patch.object(
            forms.UserCreationForm, "send_mail") as mock_send:
            response = self.client.post("/signup/", post_data)
            # response = self.client.post(reverse("signup"), post_data,content_type='application/x-www-form-urlencoded')
            # import pdb; pdb.set_trace()
        # self.assertEqual(response.status_code, 302)
        self.assertTrue(models.User.objects.filter(email="testpeterevance1@gmail.com").exists())
        self.assertTrue(auth.get_user(self.client).is_authenticated)
        mock_send.assert_called_once()
        
    def test_address_list_page_returns_only_owned(self):
        user1 = models.User.objects.create_user("user1", "Abcabc_123")
        user2 = models.User.objects.create_user("user2", "Abcabc_123")
        models.Address.objects.create(
            user=user1,
            name="peter evance",
            address="state house",
            town="Nairobi",
            county="nrb")
        models.Address.objects.create(
            user=user2,
            name="stephen omondi",
            address="Tom Mboya Ave.",
            town="Kisumu",
            county="ksm")
        self.client.force_login(user2)
        response = self.client.get(reverse("address_list"))
        self.assertEqual(response.status_code, 200)
        address_list = models.Address.objects.filter(user=user2)
        self.assertEqual(list(response.context["object_list"]),list(address_list))

    def test_address_create_stores_user(self):
        user1 = models.User.objects.create_user("user1", "Abcabc_123")
        post_data = {
            "name": "james oketch",
            "address": "likoni",
            "town": "mombasa",
            "county": "mbm"}
        self.client.force_login(user1)
        self.client.post(reverse("address_create"),post_data)
        self.assertTrue(models.Address.objects.filter(user=user1).exists())
        
    def test_add_to_basket_logged_in_works(self):
        user1 = models.User.objects.create_user("anonymous@gmail.com", "Abcd_123")
        b1 = models.Book.objects.create(
            name="The way of men",
            slug="the-way-of-men",
            price=Decimal("10.00"),
            )
        b2 = models.Book.objects.create(
            name="Microsoft Windows guide",
            slug="microsoft-windows-guide",
            price=Decimal("12.00"),
            )
        self.client.force_login(user1)
        response = self.client.get(reverse("add_to_basket"), {"book_id": b1.id})
        self.assertTrue(models.Basket.objects.filter(user=user1).exists())
        self.assertEquals(models.BasketLine.objects.filter(basket__user=user1).count(),1)
        response = self.client.get(reverse("add_to_basket"), {"book_id": b2.id})
        self.assertEquals(models.BasketLine.objects.filter(basket__user=user1).count(),2)
        self.assertEqual(response.status_code, 302)
        
    def test_add_to_basket_login_merge_works(self):
        user1 = models.User.objects.create_user("anonymous@gmail.com", "Abcd_123")
        b1 = models.Book.objects.create(
            name="The way of men",
            slug="the-way-of-men",
            price=Decimal("10.00"))
        b2 = models.Book.objects.create(
            name="Microsoft Windows guide",
            slug="microsoft-windows-guide",
            price=Decimal("12.00"))
        basket = models.Basket.objects.create(user=user1)
        models.BasketLine.objects.create(basket=basket, book=b1, quantity=3)
        response = self.client.get(reverse("add_to_basket"), {"book_id": b1.id})
        self.client.force_login(user1)
        # response = self.client.post(reverse("login"),{"email": "anonymous@gmail.com", "password": "Abcd_123"})
        self.assertTrue(auth.get_user(self.client).is_authenticated)
        self.assertTrue(models.Basket.objects.filter(user=user1).exists())
        basket = models.Basket.objects.get(user=user1)
        self.assertEquals(basket.count(),3)