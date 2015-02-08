from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import timezone
from datetime import timedelta
import json
from utils.packed_json import toJSON

def today(request):
	cTime = timezone.localtime(timezone.now())
	nextDelta = timedelta(days = 1)
	nextTime = cTime + nextDelta
	today_news = {
		"news": [
			{
			"content":"Failure is not  fatal, but failure to change might be.",
			"create_time": str(cTime.date()),
			"expired_time": str(nextTime.date()),
			},
			{
			"content":"The great use of life is to spend it for something that overlasts it."
			"create_time": str(cTime.date()),
			"expired_time": str(nextTime.date()),
			},
			{
			"content":"All you want to say will definitely be received by one in the world.\
			Would cease your desperation a little."
			"create_time": str(cTime.date()),
			"expired_time": str(nextTime.date())
			}
		],

	}
	# scrapy today news from web
	return HttpResponse(toJSON(today_news))

def latest(request):
	latest_news = [
		{"news": "No news is good news."}
	]
	# scrapy latest news from web
	return HttpResponse(toJSON(latest_news))
