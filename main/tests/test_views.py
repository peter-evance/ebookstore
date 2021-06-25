from main import forms
from django.test import TestCase
from django.urls import reverse

class TestPage(TestCase):
    '''Test for http status code = 200 OK, if respective html template is used and 
    response containing name ebookstore.
    '''
    def test_home_page_works(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, 'ebookstore')
        
        
    def test_about_us_works(self):
        response = self.client.get(reverse("about-us"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about_us.html')
        self.assertContains(response, 'ebookstore')
        
    def test_contact_us_page_works(self):
        response = self.client.get(reversr('contact_us'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact_us.html')
        self.assertContains(response, 'ebookstore')
        self.assertIsInstance(
            response.context['form'], forms.ContactUsForm
        )