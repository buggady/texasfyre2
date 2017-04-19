from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic.edit import FormView
from forms import SubmitVideoForm
from django.views import generic
from django.views.generic import ListView

from models import Videos
from django.contrib.auth.models import User
from urlparse import urlparse, parse_qs

from allauth.account.decorators import verified_email_required


class AjaxTemplateMixin(object):
 
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(self, 'ajax_template_name'):
            split = self.template_name.split('.html')
            split[-1] = '_inner'
            split.append('.html')
            self.ajax_template_name = ''.join(split)
        if request.is_ajax():
            self.template_name = self.ajax_template_name
        return super(AjaxTemplateMixin, self).dispatch(request, *args, **kwargs)

class VideosView(generic.ListView):
    template_name = 'mingle/mingle.html'
    model = Videos
    
    def get_queryset(self):
        return Videos.objects.all().order_by("category")[:25]

    def post(self, request, *args, **kwargs):

        return VideosView.as_view()

mingle = VideosView.as_view()

class SubmitVideoView(AjaxTemplateMixin, FormView):
    template_name = "mingle/submit_video.html"
    form_class = SubmitVideoForm
    success_url = '/home'

    def form_valid(self, form):
        category = form.cleaned_data['category']
        watch_url = form.cleaned_data['url']
        
        video_id = "[Bad url]" 
        if not watch_url:
            video_id = "[Add video url]"
        
        query = urlparse(watch_url)
        if query.hostname == 'youtu.be':
            video_id = query.path[1:]
        if query.hostname in ('www.youtube.com', 'youtube.com'):
            if query.path == '/watch':
                p = parse_qs(query.query)
                video_id = p['v'][0]
            if query.path[:7] == '/embed/':
                video_id = query.path.split('/')[2]
            if query.path[:3] == '/v/':
                video_id = query.path.split('/')[2]
        user = self.request.user
        new_video = Videos(category=category, watch_url=watch_url, video_id=video_id, uploader=user)
        new_video.save()
        return super(SubmitVideoView, self).form_valid(form)       

submit = SubmitVideoView.as_view()

def up_vote(request, pk):
	tmp_video = get_object_or_404(Videos, pk=pk)
	if request.user.is_authenticated():
		tmp_user = get_object_or_404(User, username=request.user.username)
		
		tmp_video.votes.up(tmp_user.id)
        tmp_video.save()

	return HttpResponseRedirect(reverse('mingle'))

def down_vote(request, pk):
    tmp_video = get_object_or_404(Videos, pk=pk)
    if request.user.is_authenticated():
        tmp_user = get_object_or_404(User, username=request.user.username)
        
        tmp_video.votes.down(tmp_user.id)
        tmp_video.save()
    return HttpResponseRedirect(reverse('mingle'))


