# from django.http.response import HttpResponseRedirect
from django.views.generic.edit import FormView
from main import forms

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