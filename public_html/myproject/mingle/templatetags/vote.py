from __future__ import absolute_import

from django import template
from django.contrib.auth.models import User
from mingle.models import Videos
from vote.models import UP

register = template.Library()

@register.assignment_tag(takes_context=True)
def vote_exists(context, video, action=UP):
    try:
        request = context['request']
        tmp_user = User.objects.get(user=request.user)
        tmp_video = Videos.objects.get(title=video.title)
    	if tmp_user.is_anonymous():
        	return False
    	#return tmp_video.votes.exists(tmp_user.id, action=action)
    	return False
    except Exception as e:
        return False
