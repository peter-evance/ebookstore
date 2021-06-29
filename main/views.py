# from django.http.response import HttpResponseRedirect
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404
from main import models, forms


class ContactUsView(FormView):
    template_name = 'contact_us.html'
    form_class = forms.ContactUsForm
    success_url = '/'

    def form_valid(self, form):
        form.send_mail()
        return super().form_valid(form)

# def contact_us(request):
#     if request.method == 'POST':
#         form = forms.ContactUsForm(request.POST)
#         if form.is_valid():
#             form.send_mail()
#             return HttpResponseRedirect('/')
#     else:
#         form = forms.ContactUsForm()
#     return render(request, 'contact_us.html', {'form': form})


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
