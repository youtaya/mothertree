from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from models import Time
from django.contrib.auth.decorators import login_required
import logging

from django.views import generic

logger = logging.getLogger(__name__)

@login_required
def index(request):
	logger.debug("request: %s" %request.user)
	#latest_time_list = Time.objects.filter(user=request.get('username'))
	latest_time_list = Time.objects.filter(handle='jinxp')
	context = {'latest_time_list': latest_time_list}

	return render(request, 'times/index.html', context)

def SyncTimes(request):
	# get user name

	pass
