from django.urls import path
from main import views


urlpatterns = [
 
    path('contact-us/', views.ContactUsView.as_view(), name='contact_us'),

]