from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from events.models import Event, EventUserRel
from django.views import generic
import os, os.path
from django.conf import settings

class IndexView(generic.ListView):
	template_name = 'events/eventsList.html'

	def get_queryset(self):
		return Event.objects.all().order_by("start_date")[:25]

class DetailView(generic.DetailView):
	model = Event

	template_name='events/eventDetails.html'

	def get_context_data(self, **kwargs):
		context = super(DetailView, self).get_context_data(**kwargs)
		tmp_user = get_object_or_404(User, username=self.request.user.username)
		tmp_event = self.get_object()

		# path joining version for other paths
		if EventUserRel.objects.filter(user=tmp_user, event=tmp_event).exists():
			context['is_current_user_registered'] = True
		else:
			context['is_current_user_registered'] = False
		
		return context
		

def rsvp(request, slug):
	tmp_event = get_object_or_404(Event, slug=slug)
	if request.user.is_authenticated():
		tmp_user = get_object_or_404(User, username=request.user.username)
		
		if not EventUserRel.objects.filter(user=tmp_user, event=tmp_event).exists():
			tmp_user_event = EventUserRel(user=tmp_user, event=tmp_event)
			tmp_user_event.save()
		else:
			tmp_user_event = EventUserRel.objects.get(user=tmp_user, event=tmp_event)
			tmp_user_event.delete()
	string = tmp_event.slug
	return HttpResponseRedirect(reverse('eventdetails', kwargs={'slug': tmp_event.slug}))