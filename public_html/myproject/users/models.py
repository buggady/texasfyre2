from django.db import models
from django.db.models import Count
from django.contrib.auth.models import User 
from allauth.account.models import EmailAddress
from events.models import Event, EventUserRel
from allauth.socialaccount.models import SocialAccount
import hashlib

class UserProfile(models.Model):

	user = models.OneToOneField(User, related_name='profile')
	#home_town = models.CharField(max_length=140, default='unknown', blank=True, null=True)
	#theme_color = models.CharField(max_length=10, default='blue')
 
	def __unicode__(self):
		return "{}'s profile".format(self.user.username)
 
	class Meta:
		db_table = 'user_profile'
		permissions = (
            ("fyr_member", "FYR Approved members"),
            ("fyr_developer", "FYR Developers")
        )
 
	#email verification
	def account_verified(self):
		if self.user.is_authenticated:
			result = EmailAddress.objects.filter(email=self.user.email)
			if len(result):
				return result[0].verified
		return False

	def top_friends(self):
		events_attended = EventUserRel.objects.filter(user=self.user)
		events_all_users = EventUserRel.objects.filter(event__in=events_attended.values('event'))
		top_friends = User.objects.filter(id__in=events_all_users.values('user_id'))
		return top_friends

	#grab facebook profile picture
	def profile_image_url(self):
		fb_uid = SocialAccount.objects.filter(user_id=self.user.id, provider='facebook')
	 
		if len(fb_uid):
			return "http://graph.facebook.com/{}/picture?width=140&height=140".format(fb_uid[0].uid)
	 
		return "http://www.gravatar.com/avatar/{}?s=140".format(hashlib.md5(self.user.email).hexdigest())

	def profile_image_url_small(self):
		fb_uid = SocialAccount.objects.filter(user_id=self.user.id, provider='facebook')
	 
		if len(fb_uid):
			return "http://graph.facebook.com/{}/picture?width=80&height=80".format(fb_uid[0].uid)
	 
		return "http://www.gravatar.com/avatar/{}?s=140".format(hashlib.md5(self.user.email).hexdigest())

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])