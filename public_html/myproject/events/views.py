from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from users.models import UserProfile
from schedule.models import Event
from events.models import EventUserRel, EventProfile
from forms import DonatePhotosForm, SubmitEventIdeaForm, SubmitPastEventForm
from django.views import generic
from django.core.mail import send_mail
import os, os.path
from django.conf import settings
import facebook_sdk
from allauth.socialaccount.models import SocialToken

from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator


class IndexView(generic.ListView):
    template_name = 'events/eventsList.html'

    def get_queryset(self):
        return Event.objects.all().order_by("start")[:25]

    @method_decorator(permission_required('users.fyr_member', login_url='/home'))
    def dispatch(self, *args, **kwargs):
        return super(IndexView, self).dispatch(*args, **kwargs)

class DetailView(generic.DetailView):
    model = EventProfile

    template_name='events/eventDetails.html'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        tmp_user = get_object_or_404(User, username=self.request.user.username)
        tmp_event_profile = self.get_object()
        try:
            token = SocialToken.objects.filter(account__user=tmp_user, account__provider='facebook')
            graph = facebook_sdk.GraphAPI(access_token=token, version='2.7')
            tmp_event_id = str(tmp_event_profile.facebook_event_id)
            facebook_data = graph.get_object(id=tmp_event_id)
            context['facebook_data'] = facebook_data
            context['fb_description'] = facebook_data['description']
            context['fb_guest_list'] = facebook_data['attending']
        except:
            context['fb_descrption'] = 'Something went wrong'
        if EventUserRel.objects.filter(user=tmp_user, event=tmp_event_profile.event).exists():
            context['is_current_user_registered'] = True
        else:
            context['is_current_user_registered'] = False
        
        return context

    @method_decorator(permission_required('users.fyr_member', login_url='/home'))
    def dispatch(self, *args, **kwargs):
        return super(DetailView, self).dispatch(*args, **kwargs)
        

def rsvp(request, slug):
    tmp_event_profile = get_object_or_404(EventProfile, slug=slug)
    if request.user.is_authenticated():
        tmp_user = get_object_or_404(User, username=request.user.username)
        
        if not EventUserRel.objects.filter(user=tmp_user, event=tmp_event_profile.event).exists():
            tmp_user_event = EventUserRel(user=tmp_user, event=tmp_event_profile.event)
            tmp_user_event.save()
        else:
            tmp_user_event = EventUserRel.objects.get(user=tmp_user, event=tmp_event_profile.event)
            tmp_user_event.delete()
    return HttpResponseRedirect(reverse('eventdetails', kwargs={'slug': tmp_event_profile.slug}))

@permission_required('users.fyr_member', login_url='/home')
def donate_photos(request, slug):
    
    message = ''

    if request.method == 'POST':
        temp_event_profile = EventProfile.objects.get(slug=slug)
        # create a form instance and populate it with data from the request:
        form = DonatePhotosForm(request.POST, request.FILES)
        if form.is_valid():
            token = SocialToken.objects.filter(account__user=request.user, account__provider='facebook')
            graph = facebook_sdk.GraphAPI(access_token=token, version='2.7')
            tmp_album_id = form.cleaned_data['facebook_album_id']
            try:
                facebook_data = graph.get_object(id=tmp_album_id)
                message = 'You gave us a real album! Now I hope you didnt give us the wrong one'
            except:
                message = 'This is not a real album ID! Try again'
    else:
        form = DonatePhotosForm()
      
    return render(request, 'events/donate_photos.html', {'form': form, 'status': message})

@permission_required('users.fyr_member', login_url='/home')
def submit_event_idea(request):
    
    message = ''

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SubmitEventIdeaForm(request.POST)
        if form.is_valid():
            name = 'test1'
            email = 'info@fyrpresents.com'
            subject = 'Event Idea'
            email_body = form.cleaned_data['title'] + ' ' + form.cleaned_data['location']

            recipients = ['info@fyrpresents.com']

            send_mail(subject, email_body, email, recipients)
            message = "Woah, this thing actually works!"
        else:
            message = "Uh Oh, we messed up somewhere"
            
    else:
        form = SubmitEventIdeaForm()

      
    return render(request, 'events/submit_event_idea.html', {'form': form, 'status': message})

@permission_required('users.fyr_member', login_url='/home')
def submit_past_event(request):
    
    message = ''

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SubmitPastEventForm(request.POST)
        if form.is_valid():
            name = 'test1'
            email = 'info@fyrpresents.com'
            subject = 'Event Idea'
            email_body = form.cleaned_data['title'] + ' ' + form.cleaned_data['location']

            recipients = ['info@fyrpresents.com']

            send_mail(subject, email_body, email, recipients)
            message = "Woah, this thing actually works!"
        else:
            message = "Uh Oh, we messed up somewhere"
            
    else:
        form = SubmitPastEventForm()

      
    return render(request, 'events/submit_past_event.html', {'form': form, 'status': message})