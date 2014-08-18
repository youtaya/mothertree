from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from bson.json_util import default, object_hook
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from muser.models import UserProfile
import json
import logging
logger = logging.getLogger(__name__)

@login_required
def luckyday(request):
	logger.debug("request: %s" %request.user)

	#luck_data = request.POST.get('luck')
	#json_list = json.loads(luck_data, object_hook=object_hook)
	current_user = User.objects.get(username=request.user)
	userProfile = current_user.get_profile()
	userProfile.luckyday = '2014/05/16'
	userProfile.save()

	return HttpResponse(200)