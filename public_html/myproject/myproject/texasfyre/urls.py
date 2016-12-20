from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.home, name='index'),
    url(r'^home', views.home, name='home'),
    url(r'^contactus', views.contactus, name='contact'),
    url(r'^about', views.about, name='about'),
	url(r'^events', views.events, name='events'),
]
