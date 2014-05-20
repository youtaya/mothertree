from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from bson.json_util import default, object_hook
import json

def recommend(request):
	recommend_friends = [
		{"friends": "wanghaia"},
	]
	# scrapy today news from web
	return HttpResponse(toJSON(recommend_friends))

def toJSON(object):
	"""Dumps the data represented by the object to JSON for wire transfer."""
	return json.dumps(object, default=default)	