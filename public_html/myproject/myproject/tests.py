from django.test import TestCase
from events.models import Event
from django.utils import timezone
from datetime import timedelta

class EventTestCase(TestCase):

    event1 = None
    event2 = None
    event3 = None

    def setUp(self):
        Event.objects.create(title="testEvent1", description="This is event 1")
        Event.objects.create(title="testEvent2", description="This is event 2", start_date=timezone.now())
        Event.objects.create(title="testEvent3", description="This is event 3", start_date=timezone.now()+timedelta(days=30))        
        self.event1 = Event.objects.get(title="testEvent1")
        self.event2 = Event.objects.get(title="testEvent2")
        self.event3 = Event.objects.get(title="testEvent3")

    def test_get_description(self):
        self.assertEqual(self.event1.description, 'This is event 1')
        self.assertEqual(self.event2.description, 'This is event 2')

    def test_in_the_past(self):
        noDateEvent = self.event1
        pastEvent = self.event2
        futureEvent = self.event3
        self.assertEqual(noDateEvent.in_the_past, "No Date Given")
        self.assertTrue(pastEvent.in_the_past)
        self.assertFalse(futureEvent.in_the_past)