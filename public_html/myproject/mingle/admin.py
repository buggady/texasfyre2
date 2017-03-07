from django.contrib import admin
from .models import Videos

class VideosAdmin(admin.ModelAdmin):
	list_display = ('category', 'watch_url', 'video_id', 'uploader', 'description')
	
admin.site.register(Videos, VideosAdmin)
