from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'monthertree.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^users/', include('users.urls', namespace='users')),
    url(r'^times/', include('times.urls', namespace="times")),
    url(r'^news/', include('news.urls', namespace="news")),
    url(r'^friends/', include('friends.urls', namespace="friends")),
    url(r'^muser/', include('muser.urls', namespace="muser")),
    url(r'^dialogs/', include('dialogs.urls', namespace="dialogs")),
)
