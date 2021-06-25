from django.views.generic.edit import FormView
from main import forms

class ContactUsView(FormView):
    template_name = 'contact_us.html'
    form_class = forms.ContactUsForm
    success_url = '/'
    
    def form_valid(self, form):
        form.send_mail()
        return super().form_valid(form)
