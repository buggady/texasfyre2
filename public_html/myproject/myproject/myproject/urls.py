from django.conf.urls import include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    #url(r'^about', views.about, name='about'),
] 

urlpatterns += staticfiles_urlpatterns()
	
