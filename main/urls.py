from os import name
from django.urls import path
from main import views


urlpatterns = [

    path('contact-us/', views.ContactUsView.as_view(), name='contact_us'),
    path('books/<slug:tag>/', views.BookListView.as_view(), name='books'),

]
