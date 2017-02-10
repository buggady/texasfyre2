from django.db import models
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress
from events.models import Event
from allauth.socialaccount.models import SocialAccount
import hashlib

class UserProfile(models.Model):
	user = models.OneToOneField(User, related_name='profile')
	home_town = models.CharField(max_length=140, default='unknown')
 
	def __unicode__(self):
		return "{}'s profile".format(self.user.username)
 
	class Meta:
		db_table = 'user_profile'
 
	#email verification
	def account_verified(self):
		if self.user.is_authenticated:
			result = EmailAddress.objects.filter(email=self.user.email)
			if len(result):
				return result[0].verified
		return False

	#grab facebook profile picture
	def profile_image_url(self):
		fb_uid = SocialAccount.objects.filter(user_id=self.user.id, provider='facebook')
	 
		if len(fb_uid):
			return "http://graph.facebook.com/{}/picture?width=140&height=140".format(fb_uid[0].uid)
			#return "http://graph.facebook.com/{}/picture?width=40&height=40".format(fb_uid[0].uid)
	 
		return "http://www.gravatar.com/avatar/{}?s=140".format(hashlib.md5(self.user.email).hexdigest())

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])