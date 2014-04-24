from django.conf.urls import patterns, url
from times import views

urlpatterns = patterns('',
	# url(r'^$', views.IndexView.as_view(), name='index'),
	# url(r'^(?P<pk>\d+)/$', views.DetailView.as_view(), name='detail'),
	# url(r'^(?P<pk>\d+)/results/$', views.ResultsView.as_view(), name='results'),

	url(r'^$', views.index, name='index'),
	url(r'^sync/$', views.sync, name="sync"),
	url(r'^reset/$', views.resetdb, name="reset"),
)