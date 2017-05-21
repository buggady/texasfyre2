from django.contrib import admin
from .models import UserProfile

#class UserProfileAdmin(admin.ModelAdmin):
#	list_display = ('user', 'home_town', 'theme_color')

admin.site.register(UserProfile)