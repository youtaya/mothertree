from django.conf.urls import patterns,url
from users import views

urlpatterns = patterns('',
	# url(r'^$', views.IndexView.as_view(), name='index'),
	# url(r'^(?P<pk>\d+)/$', views.DetailView.as_view(), name='detail'),
	# url(r'^(?P<pk>\d+)/results/$', views.ResultsView.as_view(), name='results'),

	url(r'^signup/$', views.signup, name='signup'),
	url(r'^login/$', views.login, name="login"),
	url(r'^add_avatar/$', views.add_avatar, name="add_avatar"),
	url(r'^get_avatar/$', views.get_avatar, name="get_avatar"),
	url(r'^search_people/$', views.search_people, name="search_people"),
)
