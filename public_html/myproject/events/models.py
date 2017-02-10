from django.db import models
from autoslug import AutoSlugField
from django.contrib.auth.models import User
from django.utils import timezone

class Event(models.Model):
    title = models.CharField(max_length=140)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    total_price = models.IntegerField()
    host = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = AutoSlugField(populate_from='title', editable=True)

    @property
    def in_the_past(self):
        #return False
        return timezone.now() > self.start_date 

    def guest_list(self):
        return EventUserRel.objects.filter(event=self)

    def __str__(self):
        return self.title

class EventUserRel(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    event=models.ForeignKey(Event, on_delete=models.CASCADE)
    approved=models.BooleanField(default=False)
    amount_paid=models.DecimalField(max_digits=8, decimal_places=2, default=0)
