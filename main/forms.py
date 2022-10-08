import logging
from django import forms
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.contrib.auth.forms import UsernameField
from django.core.mail import send_mail
from .models import User,Basket,BasketLine, Address
from django.contrib.auth import authenticate
from django.forms import widgets, inlineformset_factory
from . import widgets

logger = logging.getLogger(__name__)


class UserCreationForm(DjangoUserCreationForm):
    class Meta(DjangoUserCreationForm.Meta):
        model = User
        fields = ("email",)
        field_classes = {"email": UsernameField}
        
    def send_mail(self):
        logger.info("Sending signup email for email {}".format(self.cleaned_data['email']))
        message = "Welcome {}".format(self.cleaned_data['email'])
        send_mail("Welcome to ebookstore",
                  message,"site@ebookstore.domain",
                  [self.cleaned_data["email"]],fail_silently=True,)
        

class AuthenticationForm(forms.Form):
    email = forms.EmailField
    password = forms.CharField(strip=False, widget=forms.PasswordInput)

    def __init__(self, request=None,*args,**kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def get_user(self):
        return self.user
        
    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        
        if email is not None and password:
            self.user = authenticate(self.request, email=email, password=password)
            if self.user is None:
                raise forms.ValidationError("Incorrect email or password combination.") 
            logger.info("Login successful for email %s", email)   
        return self.cleaned_data
    
    


class ContactUsForm(forms.Form):
    name = forms.CharField(label='Your name', max_length=100, required=True)
    message = forms.CharField(label='Tell us something', max_length=600, widget=forms.Textarea, required=True)
    
    def send_mail(self):
        logger.info("Sending email to customer service...")
        message = "From: {0}\nMessage: {1}".format(self.cleaned_data["name"],self.cleaned_data["message"])
        send_mail("Site message",message,"site@ebookstore.domain",["customerservice@ebookstore.doman"],fail_silently=False)

BasketLineFormSet = inlineformset_factory(
    Basket,
    BasketLine,
    fields=("quantity",),
    extra=0,widgets={"quantity":widgets.PlusMinusNumberInput()})

class AddressSelectionForm(forms.Form):
    billing_address = forms.ModelChoiceField(queryset=None)
    shipping_address = forms.ModelChoiceField(queryset=None)
    
    def __init__(self, user, *args, **kwargs):
        super(). __init__(*args, **kwargs)
        queryset = Address.objects.filter(user=user)
        self.fields['billing_address'].queryset = queryset
        self.fields['shipping_address'].queryset = queryset