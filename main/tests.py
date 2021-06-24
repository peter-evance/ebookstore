from django.test import TestCase

class TestPage(TestCase):
    '''Test for http status code = 200 OK, if respective html template is used and 
    response containing name ebookstore.
    '''
    def test_home_page_works(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, 'ebookstore')
        
        
    def test_about_us_works(self):
        response = self.client.get('/about-us/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about_us.html')
        self.assertContains(response, 'ebookstore')