from django.shortcuts import render
from django.core.mail import send_mail
from forms import ContactForm

def home(request):
    return render(request, 'texasfyre/home.html')

def about(request):
   return render(request, 'texasfyre/about.html')

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
      
    return render(request, 'texasfyre/contact.html', {'form': form, 'status': message})