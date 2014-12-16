from django.conf.urls import patterns, url
from dialogs import views

urlpatterns = patterns('',
	# url(r'^$', views.IndexView.as_view(), name='index'),
	# url(r'^(?P<pk>\d+)/$', views.DetailView.as_view(), name='detail'),
	# url(r'^(?P<pk>\d+)/results/$', views.ResultsView.as_view(), name='results'),
	
	url(r'^reset/$', views.resetdb, name="reset"),
	url(r'^share/$', views.share, name="share"),
	url(r'^getdialog/$', views.get_dialog, name="getdialog"),
)
