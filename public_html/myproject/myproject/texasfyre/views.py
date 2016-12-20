from django.shortcuts import render

def home(request):
	return render(request, 'texasfyre/home.html')

def about(request):
   return render(request, 'texasfyre/about.html')

def contactus(request):
   return render(request, 'texasfyre/contactus.html')

def events(request):
   return render(request, 'texasfyre/events.html')

