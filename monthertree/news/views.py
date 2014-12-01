from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import timezone
from datetime import timedelta
import json

def today(request):
	cTime = timezone.localtime(timezone.now())
	nextDelta = timedelta(days = 1)
	nextTime = cTime + nextDelta
	today_news = {
		"news": [
			{"info":"Failure is not  fatal, but failure to change might be."},
			{"info":"The great use of life is to spend it for something that overlasts it."},
			{"info":"All you want to say will definitely be received by one in the world.\
			Would cease your desperation a little."}
		],
		"create_time": str(cTime.date()),
		"expired_time": str(nextTime.date())
	}
	# scrapy today news from web
	return HttpResponse(toJSON(today_news))

def latest(request):
	latest_news = [
		{"news": "No news is good news."}
	]
	# scrapy latest news from web
	return HttpResponse(toJSON(latest_news))

def toJSON(object):
	"""Dumps the data represented by the object to JSON for wire transfer."""
	return json.dumps(object, ensure_ascii=False)
