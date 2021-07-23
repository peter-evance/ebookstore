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
        response = self.client.get('/home/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, 'ebookstore')

    def test_about_us_works(self):
        # response = self.client.get(reverse("about-us"))
        response = self.client.get('/about_us/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about_us.html')
        self.assertContains(response, 'ebookstore')

    def test_contact_us_page_works(self):
        # response = self.client.get(reverse('contact_us'))
        response = self.client.get('/contact_us/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact_us.html')
        self.assertContains(response, 'ebookstore')
        self.assertIsInstance(
            response.context['form'], forms.ContactUsForm)

    def test_products_page_returns_active(self):
        models.Book.objects.create(
            name="The cathedral and the bazaar",
            slug="cathedral-bazaar",
            price=Decimal("10.00"),)
        models.Product.objects.create(
            name="A Tale of Two Cities",
            slug="tale-two-cities",
            price=Decimal("2.00"),
            active=False,)
        response = self.client.get(
            reverse("books", kwargs={"tag": "all"}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ebookstore")
        book_list = models.Book.objects.active().order_by("name")
        self.assertEqual(
            list(response.context["object_list"]), list(book_list))

    def test_products_page_filters_by_tags_and_active(self):
        cb = models.Book.objects.create(
            name="The cathedral and the bazaar",
            slug="cathedral-bazaar",
            price=Decimal("10.00"))
        cb.tags.create(name="Open source", slug="opensource")
        models.Book.objects.create(
            name="Microsoft Windows guide",
            slug="microsoft-windows-guide",
            price=Decimal("12.00"))
        response = self.client.get(
            reverse("books", kwargs={"tag": "opensource"}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ebookstore")
        book_list = (models.Book.objects.active().filter(
            tags__slug="opensource").order_by("name"))
        self.assertEqual(
            list(response.context["object_list"]), list(book_list))

    def test_user_signup_page_loads_correctly(self):
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "signup.html")
        self.assertContains(response, "ebookstore")
        self.assertIsInstance(
            response.context["form"], forms.UserCreationForm
            )
    
    def test_user_signup_page_submission_works(self):
        post_data = {
            "email": "peterevance1@gmail.com",
            "password1": "abcabcabc",
            "password2": "abcabcabc",
            }
        with patch.object(
            forms.UserCreationForm, "send_mail"
            ) as mock_send:
            response = self.client.post(
                reverse("signup"), post_data
                )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            models.User.objects.filter(
                email="peterevance1@gmail.com"
            ).exists()
        )
        self.assertTrue(
            auth.get_user(self.client).is_authenticated
        )
        mock_send.assert_called_once()
        
    def test_address_list_page_returns_only_owned(self):
        user1 = models.User.objects.create_user(
            "user1", "abcabc123"
            )
        user2 = models.User.objects.create_user(
            "user2", "abcabc123"
            )
        models.Address.objects.create(
            user=user1,
            name="peter evance",
            address1="flat 2",
            address2="moi avenue",
            city="Nairobi",
            county="nrb",
            )
        models.Address.objects.create(
            user=user2,
            name="stephen omondi",
            address1="Tom Mboya Ave.",
            city="Kisumu",
            county="ksm",
            )
        self.client.force_login(user2)
        response = self.client.get(reverse("address_list"))
        self.assertEqual(response.status_code, 200)
        address_list = models.Address.objects.filter(user=user2)
        self.assertEqual(list(response.context["object_list"]),list(address_list))

    def test_address_create_stores_user(self):
        user1 = models.User.objects.create_user(
            "user1", "abcabc123"
            )
        post_data = {
            "name": "james oketch",
            "address1": "Likoni",
            "address2": "",
            "zip_code": "MA12GS",
            "city": "Mombasa",
            "county": "mbm",
            }
        self.client.force_login(user1)
        self.client.post(reverse("address_create"),post_data)
        self.assertTrue(models.Address.objects.filter(user=user1).exists())