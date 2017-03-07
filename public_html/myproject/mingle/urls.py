from django.conf.urls import url, include
from . import views

urlpatterns = [
	url(r'^$', views.mingle, name='mingle'),
	url(r'^(?P<pk>\d+)/upvote$', views.up_vote, name='up_vote'),
	url(r'^(?P<pk>\d+)/downvote$', views.down_vote, name='down_vote'),
	url(r'^submit/', views.submit, name='submit_video'),
]
