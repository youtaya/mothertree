from django.conf.urls import patterns, url
from news import views

urlpatterns = patterns('',
	# url(r'^$', views.IndexView.as_view(), name='index'),
	# url(r'^(?P<pk>\d+)/$', views.DetailView.as_view(), name='detail'),
	# url(r'^(?P<pk>\d+)/results/$', views.ResultsView.as_view(), name='results'),

	url(r'^today/$', views.today, name='today'),
	url(r'^latest/$', views.latest, name="latest"),
)
