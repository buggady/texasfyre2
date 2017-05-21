from django.db import models
from autoslug import AutoSlugField
from django.utils.text import slugify
from django.contrib.auth.models import User
from annoying.fields import AutoOneToOneField
from django.utils import timezone

from schedule.models import Event
from taggit.managers import TaggableManager
from photologue.models import Gallery

class EventProfile(models.Model):

    CATEGORY_CHOICES = (
        ('general', 'General'),
        ('vacation', 'Vacation'), #a64d79
        ('festival', 'Festival'), #3d85c6
        ('camping', 'Camping'), #6aa84f
        ('entertainment', 'Entertainment'), #cc0000
        ('show', 'Show'), #274e13
    )

    event = AutoOneToOneField(Event, primary_key=True, related_name='profile')
    slug = AutoSlugField(unique=True, editable=True)
    category = models.CharField(max_length=14, choices=CATEGORY_CHOICES, default='general')
    private = models.BooleanField(default=True)
    location = models.CharField(max_length=140, default="Don't Know")
    total_price = models.IntegerField(default="0")
    host = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    facebook_event_id = models.CharField(max_length=100, null=True, blank=True)
    gallery = models.ForeignKey(Gallery, on_delete=models.SET_NULL, blank=True, null=True)

    #tags = TaggableManager()

    @property
    def in_the_past(self):
        if self.event.end:
            return timezone.now() > self.event.end
        return "No Date Given"   

    def guest_list(self):
        return EventUserRel.objects.filter(event=self.event)

    def guest_count(self):
        return len(EventUserRel.objects.filter(event=self.event))

    def fb_page(self):
        return "https://www.facebook.com/events/{}".format(self.facebook_event_id)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.event.title)
        super(EventProfile, self).save(*args, **kwargs)

    def __str__(self):
        return self.event.title

class EventUserRel(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    event=models.ForeignKey(Event, on_delete=models.CASCADE)
    approved=models.BooleanField(default=False)
    amount_paid=models.DecimalField(max_digits=8, decimal_places=2, default=0)