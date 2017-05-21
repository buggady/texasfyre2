from django.contrib import admin
from events.models import EventProfile, EventUserRel

class EventProfileAdmin(admin.ModelAdmin):
    list_display = ('get_title', 'category', 'location', 'total_price')

    def get_title(self, obj):
        return obj.event.title
    get_title.short_description = 'Title'
    get_title.admin_order_field = 'event__title'

class EventUserRelAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'amount_paid')

admin.site.register(EventUserRel, EventUserRelAdmin)
admin.site.register(EventProfile, EventProfileAdmin)
