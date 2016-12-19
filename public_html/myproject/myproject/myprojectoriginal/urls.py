from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views

urlpatterns = [
	url(r'^$', views.base, name='base'),
	url(r'^home', views.home, name='home'),
	url(r'^about', views.about, name='about'),
	url(r'^events', views.events, name='events'),
	url(r'^contact', views.contact, name='contact'),
	url(r'^admin/', admin.site.urls),
] 

urlpatterns += staticfiles_urlpatterns()
	
