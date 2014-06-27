from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from bson.json_util import default, object_hook
import json
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

def recommend(request):
	recommend_friends = []
	friends = User.objects.all()
	for friend in friends:
		if(friend.username == "root"):
			continue
		logger.debug("friend is : %s" %friend.username)
		recommend = {'friends': friend.username}
		recommend_friends.append(recommend)
	# scrapy today news from web
	return HttpResponse(toJSON(recommend_friends))

def toJSON(object):
	"""Dumps the data represented by the object to JSON for wire transfer."""
	return json.dumps(object, default=default)	