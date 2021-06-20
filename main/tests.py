from django.test import TestCase

# Create your tests here.

class TestPage(TestCase):
    '''Test for http status code = 200 OK,
    home.html template used and response containing name of the bookshop
    '''
    def test_home_page_works(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, 'ebookstore')