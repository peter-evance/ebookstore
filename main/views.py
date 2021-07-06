import logging
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404
from main import models, forms


logger = logging.getLogger(__name__)


class SignupView(FormView):
    template_name = "signup.html"
    form_class = forms.UserCreationForm
    
    def get_success_url(self):
        redirect_to = self.request.GET.get("next", "/")
        return redirect_to
    
    def form_valid(self, form):
        response = super().form_valid(form)
        form.save()
        
        email = form.cleaned_data.get("email")
        raw_password = form.cleaned_data.get("password1")
        logger.info(
            "New signup for email=%s through SignupView", email
            )
        user = authenticate(email=email, password=raw_password)
        login(self.request, user)
        form.send_mail()
        messages.info(
            self.request, "You signed up successfully."
            )
        return response



class ContactUsView(FormView):
    template_name = 'contact_us.html'
    form_class = forms.ContactUsForm
    success_url = '/'

    def form_valid(self, form):
        form.send_mail()
        return super().form_valid(form)


class BookListView(ListView):
    '''Depending on the content of kwargs, this view returns a
list of active books belonging to that tag, or simply all active ones if the
tag all is specified'''
    template_name = "main/book_list.html"
    paginate_by = 5

    def get_queryset(self):
        tag = self.kwargs['tag']
        self.tag = None
        if tag != "all":
            self.tag = get_object_or_404(
                models.BookTag, slug=tag)
        if self.tag:
            books = models.Book.objects.active().filter(tags=self.tag)
        else:
            books = models.Book.objects.active()
        return books.order_by("name")
