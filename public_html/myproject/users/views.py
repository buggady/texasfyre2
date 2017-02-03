from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from events.models import Event, EventUserRel
from django.views import generic
from datetime import date
from djstripe.models import Customer

class UserEventsListView(generic.ListView):
	template_name = 'users/profile.html'

	def get_queryset(self):
		try:
			tmp_user_rel = EventUserRel.objects.filter(user=self.request.user)
		except:
			tmp_user_rel = EventUserRel.objects.none()
		
		return tmp_user_rel

class UserEventsDetailsView(generic.DetailView):
	model = EventUserRel

	template_name = 'users/usereventsdetails.html'

def pay_for_event(request, pk):
	if request.user.is_authenticated():
		user = get_object_or_404(User, username=request.user.username)
		eventuserrel = get_object_or_404(EventUserRel, pk=pk)
		customer, created = Customer.get_or_create(subscriber=user)

		amount = Decimal(10.00)
		customer.charge(amount)
		eventuserrel.amount_paid += amount
		eventuserrel.save()
		
	return HttpResponseRedirect(reverse('user_event_details', args=(pk)))