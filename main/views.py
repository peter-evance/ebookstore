import logging
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.shortcuts import render,get_object_or_404
from django.urls import reverse_lazy,reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from main import models, forms
from django import forms as django_forms
from django.db import models as django_models
import django_filters
from django_filters.views import FilterView


logger = logging.getLogger(__name__)


class SignupView(FormView):
    template_name = "signup.html"
    form_class = forms.UserCreationForm
    # success_url = reverse_lazy("next")
    
    def get_success_url(self):
        redirect_to = self.request.GET.get("next", "/")
        return redirect_to
    
    def form_valid(self, form):
        response = super().form_valid(form)
        form.save()
        email = form.cleaned_data.get("email")
        raw_password = form.cleaned_data.get("password1")
        logger.info("\n****\nNew signup for email (%s) through SignupView", email)
        user = authenticate(email=email, password=raw_password)
        login(self.request, user)
        form.send_mail()
        messages.info(self.request, "You signed up successfully.")
        return response


class ContactUsView(FormView):
    template_name = 'contact_us.html'
    form_class = forms.ContactUsForm
    success_url = '/'

    def form_valid(self, form):
        form.send_mail()
        return super().form_valid(form)


class BookListView(ListView):
    '''
    Depending on the content of kwargs, this view returns a 
    list of active books belonging to that tag, or simply all active ones if the
    tag all is specified
    '''
    template_name = "book_list.html"
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
    template_name = "address_select.html"
    model = models.Address
    
    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class AddressCreateView(LoginRequiredMixin, CreateView):
    model = models.Address
    template_name = "address_create.html"
    success_url = reverse_lazy("address_list")
    fields = ["name","address","town","county",]
    
    def form_valid(self, form):
        obj= form.save(commit=False)
        obj.user= self.request.user
        obj.save()
        return super().form_valid(form)

       
class AddressUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Address
    template_name = "address_update.html"
    success_url = reverse_lazy("address_list")
    fields = ["name","address","town","county",]
    
    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)
 
    
class AddressDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Address
    template_name = "address_confirm_delete.html"
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
    basketline, created = models.BasketLine.objects.get_or_create(basket=basket, book=book)
    if not created:
        basketline.quantity += 1
        basketline.save()
    return HttpResponseRedirect(reverse("book", args=(book.slug,)))

def manage_basket(request):
    formset = forms.BasketLineFormSet(instance=request.basket)
    if not request.basket:
        return render(request, "basket.html", {"formset": None})
    if request.method == "POST":
        formset = forms.BasketLineFormSet(request.POST, instance=request.basket)
        if formset.is_valid():
            formset.save()
        else:
            formset
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
            form.cleaned_data['shipping_address'])
        return super().form_valid(form)
    
        
class DateInput(django_forms.DateInput):
    input_type = 'date'
    
class OrderFilter(django_filters.FilterSet):
    class Meta:
        model = models.Order
        fields = {
                'user__email': ['icontains'],
                'status': ['exact'],
                # 'date_updated': ['gt', 'lt'],
                # 'date_added': ['gt', 'lt'],
                }
        filter_overrides = {
                django_models.DateTimeField: {
                    'filter_class': django_filters.DateFilter,
                    'extra': lambda f:{'widget': DateInput}}}

class OrderView(UserPassesTestMixin, FilterView):
    filterset_class = OrderFilter
    login_url = reverse_lazy("login")
    
    def test_func(self):
        return self.request.user.is_staff is True