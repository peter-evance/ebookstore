import logging
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.views.generic.edit import FormView, CreateView,UpdateView,DeleteView
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404,render
from django.urls import reverse_lazy,reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from main import models, forms
from django.http import HttpResponseRedirect


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

class AddressListView(LoginRequiredMixin, ListView):
    model = models.Address
    
    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

class AddressCreateView(LoginRequiredMixin, CreateView):
    model = models.Address
    fields = [
        "name",
        "address1",
        "address2",
        "zip_code",
        "city",
        "county",
    ]
    
    success_url = reverse_lazy("address_list")
    
    def form_valid(self, form):
        obj= form.save(commit=False)
        obj.user= self.request.user
        obj.save()
        return super().form_valid(form)
    
    
class AddressUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Address
    
    fields = [
        "name",
        "address1",
        "address2",
        "zip_code",
        "city",
        "county",
        ]
    
    success_url = reverse_lazy("address_list")
    
    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)
    
class AddressDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Address
    
    success_url = reverse_lazy("address_list")
    
    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)
    
    
def add_to_basket(request):
    book = get_object_or_404(models.Book, pk=request.GET.get("book_id"))
    basket = request.basket
    if not request.basket:
        if request.user.is_authenticated:
            user = request.user
        else:
            user = None
            basket = models.Basket.objects.create(user=user)
            request.session["basket_id"] = basket.id
            basketline, created = models.BasketLine.objects.get_or_create(
                basket=basket, book=book
                )
            if not created:
                basketline.quantity += 1
                basketline.save()
                return HttpResponseRedirect(
                    reverse("book", args=(book.slug,)))

def manage_basket(request):
    if not request.basket:
        return render(request, "basket.html", {"formset": None})
    if request.method == "POST":
        formset = forms.BasketLineFormSet(
            request.POST, instance=request.basket
            )
        if formset.is_valid():
            formset.save()
        else:
            formset = forms.BasketLineFormSet(
                instance=request.basket
                )
    if request.basket.is_empty():
        return render(request, "basket.html", {"formset": None})
    return render(request, "basket.html", {"formset": formset})

class AddressSelectionView(LoginRequiredMixin, FormView):
    template_name = "address_select.html"
    form_class = forms.AddressSelectionForm
    success_url = reverse_lazy('checkout_done')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        del self.request.session['basket_id']
        basket = self.request.basket
        basket.create_order(
            form.cleaned_data['billing_address'],
            form.cleaned_data['shipping_address']
            )
        return super().form_valid(form)