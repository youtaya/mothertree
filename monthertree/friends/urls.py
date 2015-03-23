from django.conf.urls import patterns, url
from friends import views

urlpatterns = patterns('',
	# url(r'^$', views.IndexView.as_view(), name='index'),
	# url(r'^(?P<pk>\d+)/$', views.DetailView.as_view(), name='detail'),
	# url(r'^(?P<pk>\d+)/results/$', views.ResultsView.as_view(), name='results'),

	url(r'^recommend/$', views.recommend, name="recommend"),
	url(r'^add_friend/$', views.add_friend, name="add_friend"),
	url(r'^accept_friend/$', views.accept_friend, name="accept_friend"),
	url(r'^update_friend/$', views.update_friend, name="update_friend"),
	url(r'^sync_friend/$', views.sync_friend, name="sync_friend"),
)
