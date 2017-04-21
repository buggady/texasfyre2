from django.contrib import admin
from events.models import Event, EventUserRel

class EventAdmin(admin.ModelAdmin):
	list_display = ('title', 'category', 'start_date', 'location', 'total_price')

class EventUserRelAdmin(admin.ModelAdmin):
	list_display = ('user', 'event', 'amount_paid')

admin.site.register(Event, EventAdmin)
admin.site.register(EventUserRel, EventUserRelAdmin)
