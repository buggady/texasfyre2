from django.shortcuts import render
from django.core.mail import send_mail
from forms import ContactForm

def home(request):
   return render(request, 'home.html')

def about(request):
   return render(request, 'about.html')

def contact(request):
   
    form = ContactForm()
    message = ' '

    if request.method == 'POST':
        
        # create a form instance and populate it with data from the request:
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            recipients = ['info@texasfyre.com']

            send_mail(subject, message, email, recipients)
            message = 'You did something right!'
      
    return render(request, 'contact.html', {'form': form, 'status': message})

class AjaxTemplateMixin(object):
 
     def dispatch(self, request, *args, **kwargs):
         if not hasattr(self, 'ajax_template_name'):
             split = self.template_name.split('.html')
             split[-1] = '_inner'
             split.append('.html')
             self.ajax_template_name = ''.join(split)
         if request.is_ajax():
             self.template_name = self.ajax_template_name
         return super(AjaxTemplateMixin, self).dispatch(request, *args, **kwargs)