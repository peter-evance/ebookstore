from django import forms
from django.core.mail import send_mail
import logging

logger = logging.getLogger(__name__)


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
        