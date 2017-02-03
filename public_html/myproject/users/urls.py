from django.conf.urls import url, include
from django.views.generic import ListView, DetailView
from users import views

urlpatterns = [
	url(r'^$', views.UserEventsListView.as_view(), name='userprofile'),
	url(r'^(?P<pk>\d+)$', views.UserEventsDetailsView.as_view(), name='user_event_details'),
	url(r'^(?P<pk>\d+)/submit-payment$', views.pay_for_event, name='pay_for_event'),
]