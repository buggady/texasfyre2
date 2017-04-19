from django.db import models
from autoslug import AutoSlugField
from django.contrib.auth.models import User
from vote.models import VoteModel

from taggit.managers import TaggableManager

class Videos(VoteModel, models.Model):
	CATEGORY_CHOICES = (
		('general', 'General'),
        ('djset', 'DJ Set'),
        ('trippy', 'Trippy'),
    )

	title = models.CharField(max_length=50, default='No Title')
	description = models.CharField(max_length=140, blank=True)
	uploader = models.ForeignKey(User, on_delete=models.CASCADE)
	category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='general')
	watch_url = models.URLField(max_length=200)
	video_id = models.CharField(max_length=100)
	slug = AutoSlugField(populate_from='title', editable=True)

	tags = TaggableManager()
