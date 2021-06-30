from os import name
from django.views.generic.detail import DetailView
from django.urls import path
from main import models, views


urlpatterns = [

    path('contact-us/', views.ContactUsView.as_view(), name='contact_us'),
    path('books/<slug:tag>/', views.BookListView.as_view(), name='books'),
    path('book/<slug:slug>/', DetailView.as_view(model=models.Book), name='book')

]
