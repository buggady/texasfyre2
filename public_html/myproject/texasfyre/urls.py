from django.conf.urls import url, include
from . import views

urlpatterns = [
	url(r'^$', views.home, name='index'),
	url(r'^home', views.home, name='home'),
	url(r'^contact', views.contact, name='contact'),
	url(r'^about', views.about, name='about'),
]
