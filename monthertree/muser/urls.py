from django.conf.urls import patterns, url
from muser import views

urlpatterns = patterns('',
	# url(r'^$', views.IndexView.as_view(), name='index'),
	# url(r'^(?P<pk>\d+)/$', views.DetailView.as_view(), name='detail'),
	# url(r'^(?P<pk>\d+)/results/$', views.ResultsView.as_view(), name='results'),

	url(r'^luckyday/$', views.luckyday, name="luckyday"),
	url(r'^getday/$', views.getday, name="getday"),
)