from decimal import Decimal
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from schedule.models import Event
from events.models import Event, EventUserRel
from users.models import UserProfile
from django.views import generic
from datetime import date
from forms import EditProfileForm
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator

import facebook_sdk
from allauth.socialaccount.models import SocialToken

class UserEventsListView(generic.ListView):
    template_name = 'users/profile.html'

    def get_queryset(self):
        try:
            tmp_user_rel = EventUserRel.objects.filter(user=self.request.user)
            events_attended = Event.objects.filter(id__in=tmp_user_rel.values('event_id'))
        except:
            events_attended = Event.objects.none()
        
        return events_attended

    @method_decorator(permission_required('users.fyr_member', login_url='/home'))
    def dispatch(self, *args, **kwargs):     
        return super(UserEventsListView, self).dispatch(*args, **kwargs)

class UserEventsDetailsView(generic.DetailView):
    model = EventUserRel

    template_name = 'users/usereventsdetails.html'

    @method_decorator(permission_required('users.fyr_member', login_url='/home'))
    def dispatch(self, *args, **kwargs):
        return super(UserEventsDetailsView, self).dispatch(*args, **kwargs)

@permission_required('users.fyr_member', login_url='/home')
def edit_profile(request):
    data = {'first_name': request.user.first_name, 
            'last_name': request.user.last_name,
            #'home_town': request.user.profile.home_town
            }
    form = EditProfileForm(initial=data)
    message = ' '

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = EditProfileForm(request.POST)
        if form.is_valid():
            user = get_object_or_404(User, username=request.user.username)
            profile = get_object_or_404(UserProfile, user=user)
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            #profile.home_town = form.cleaned_data['home_town']
            #profile.theme_color = request.COOKIES.get('mysheet', 'jade') 
            user.save()
            profile.save()

            message = 'You did something right!'
      
    return render(request, 'users/editprofile.html', {'form': form, 'status': message})