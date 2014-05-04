from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'monthertree.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^account/', include('account.urls')),
    url(r'^times/', include('times.urls', namespace="times")),
    url(r'^news/', include('news.urls', namespace="news")),
    url(r"^$", TemplateView.as_view(template_name="homepage.html"), name="home"),
)
