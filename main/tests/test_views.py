from main import forms, models
from django.test import TestCase
from django.urls import reverse
from decimal import Decimal


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
