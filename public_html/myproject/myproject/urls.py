from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.contrib.auth.views import logout
from oscar.app import application

urlpatterns = [
	url(r'^', include('texasfyre.urls')),
	url(r'^events/', include('events.urls')),
	url(r'^user/', include('users.urls')),
	url(r'^mingle/', include('mingle.urls')),
	url(r'^market/', include(application.urls)),
	url(r'^accounts/logout/$', logout,{'next_page': '/'}),
	url(r'^accounts/', include('allauth.urls')),
	url(r'^photologue/', include('photologue.urls', namespace='photologue')),
	url(r'^newsletter/', include('newsletter.urls')),
	url(r'^i18n/', include('django.conf.urls.i18n')),
	url(r'^admin_tools/', include('admin_tools.urls')),
	url(r'^admin/', admin.site.urls),
] 

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^debug/', include(debug_toolbar.urls)),
        url(r'^explorer/', include('explorer.urls')),
    ]
	
