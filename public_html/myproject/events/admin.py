from django.contrib import admin
from events.models import Event, EventUserRel

class EventUserRelAdmin(admin.ModelAdmin):
	list_display = ('user', 'event', 'amount_paid')
admin.site.register(Event)
admin.site.register(EventUserRel, EventUserRelAdmin)
