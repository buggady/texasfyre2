from django.shortcuts import render

def mingle(request):
   return render(request, 'mingle/mingle.html')