from django.db import models
from autoslug import AutoSlugField
from django.contrib.auth.models import User
from django.utils import timezone

from taggit.managers import TaggableManager
from photologue.models import Gallery

class Event(models.Model):
    title = models.CharField(max_length=140)
    description = models.TextField(null=True)
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)
    total_price = models.IntegerField(default="0")
    host = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    slug = AutoSlugField(populate_from='title', editable=True)

    gallery = models.OneToOneField(Gallery,null=True)

    tags = TaggableManager()

    @property
    def in_the_past(self):
        if self.start_date:
            return timezone.now() > self.start_date 
        return "No Date Given"

    def guest_list(self):
        return EventUserRel.objects.filter(event=self)

    def __str__(self):
        return self.title

class EventUserRel(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    event=models.ForeignKey(Event, on_delete=models.CASCADE)
    approved=models.BooleanField(default=False)
    amount_paid=models.DecimalField(max_digits=8, decimal_places=2, default=0)
