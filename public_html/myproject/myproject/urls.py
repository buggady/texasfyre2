from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings

urlpatterns = [
	url(r'^admin/', admin.site.urls),
	url(r'^', include('texasfyre.urls')),
	url(r'^events/', include('events.urls')),
	url(r'^user/', include('users.urls')),
	url(r'^mingle/', include('mingle.urls')),
	url(r'^market/', include('market.urls')),
	url(r'^accounts/logout/$', 'django.contrib.auth.views.logout',{'next_page': '/'}),
	url(r'^accounts/', include('allauth.urls')),
	url(r'^photologue/', include('photologue.urls', namespace='photologue')),
	url(r'^payments/', include('djstripe.urls', namespace="djstripe")),
	url(r'^newsletter/', include('newsletter.urls')),
] 

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^debug/', include(debug_toolbar.urls)),
        url(r'^explorer/', include('explorer.urls')),
    ]
	
