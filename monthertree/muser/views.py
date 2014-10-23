from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from muser.models import UserProfile
import json
import logging
logger = logging.getLogger(__name__)

#@login_required
def luckyday(request):
	#logger.debug("request: %s" %request.user)


	luck_data = request.POST.get('luck')
	json_list = json.loads(luck_data)
	#current_user = User.objects.get(username=request.user)
	current_user = User.objects.get(username=json_list[0]["username"])
	userProfile = current_user.get_profile()
	userProfile.luckyday = json_list[0]["date"]
	userProfile.save()

	return HttpResponse(200)

#@login_required
def getday(request):
	#logger.debug("request: %s" %request.user)

	luck_data = request.POST.get('luck')
	json_list = json.loads(luck_data)
	#current_user = User.objects.get(username=request.user)
	current_user = User.objects.get(username=json_list[0]["username"])
	userProfile = current_user.get_profile()
	lucky_date  = userProfile.luckyday
	ret_data = [
		{"luckyday": str(lucky_date)},
	]
	return HttpResponse(toJSON(ret_data))

def toJSON(object):
	"""Dumps the data represented by the object to JSON for wire transfer."""
	return json.dumps(object, ensure_ascii=False)
