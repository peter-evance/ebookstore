import logging
from django import forms
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.contrib.auth.forms import UsernameField
from django.core.mail import send_mail
from .models import User



logger = logging.getLogger(__name__)


class UserCreationForm(DjangoUserCreationForm):
    class Meta(DjangoUserCreationForm.Meta):
        model = User
        fields = ("email",)
        field_classes = {"email": UsernameField}
        
    def send_mail(self):
        logger.info(
            f"Sending signup email for email {self.cleaned_data['email']}"
        )
        message = f"Welcome {self.cleaned_data['email']}"
        send_mail(
            "Welcome to ebookstore",
            message,
            "site@booktime.domain",
            [self.cleaned_data["email"]],
        fail_silently=True,
        )
        






class ContactUsForm(forms.Form):
    name = forms.CharField(label='Your name', max_length=100, required=True)
    message = forms.CharField(label='Tell us something', max_length=600, widget=forms.Textarea, required=True)
    
    def send_mail(self):
        logger.info("Sending email to customer service")
        message = "From {0} \n{1}".format(self.cleaned_data["name"],self.cleaned_data["message"])
        
        send_mail(
            "Site message",
            message,
            "site@ebookstore.domain",
            ["customerservice@ebookstore.doman"],
            fail_silently=False
        )
        