from django.conf.urls import url, include
from django.views.generic import ListView, DetailView
from events import views as events_views

urlpatterns = [
	url(r'^$', events_views.IndexView.as_view(), name='eventslist'),
	url(r'^submit-event-idea', events_views.submit_event_idea, name='submit_event_idea'),
	url(r'^submit-past-event', events_views.submit_past_event, name='submit_past_event'),
	url(r'^(?P<slug>[\w-]+)$', events_views.DetailView.as_view(), name='eventdetails'),
	url(r'^(?P<slug>[\w-]+)/rsvp', events_views.rsvp, name='rsvp_to_event'),
	url(r'^(?P<slug>[\w-]+)/donate-photos', events_views.donate_photos, name='donate_photos'),
]
