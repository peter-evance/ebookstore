from django.urls import path
from . import views


urlpatterns = [
    path("customer-service/<int:order_id>/",views.room, name="cs_chat"),
    ]
