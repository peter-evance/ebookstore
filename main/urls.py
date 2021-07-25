from django.views.generic.detail import DetailView
from django.urls import path
from main import models, views, forms
from django.contrib.auth.views import LoginView


urlpatterns = [
    path('signup/', views.SignupView.as_view(), name="signup"),
    path('login/', LoginView.as_view(template_name="login.html", form_class=forms.AuthenticationForm), name="login"),
    path('contact-us/', views.ContactUsView.as_view(), name='contact_us'),
    path('address/', views.AddressListView.as_view(), name="address_list"),
    path('address/create/', views.AddressCreateView.as_view(), name="address_create"),
    path('address/<int:pk>/',views.AddressUpdateView.as_view(),name="address_update"),
    path('address/<int:pk>/delete/',views.AddressDeleteView.as_view(),name="address_delete"),
    path('books/<slug:tag>/', views.BookListView.as_view(), name='books'),
    path('book/<slug:slug>/', DetailView.as_view(model=models.Book), name='book'),
    path('basket/',views.manage_basket,name="basket"),
    path('add-to-basket/',views.add_to_basket, name="add_to_basket")
    

]
