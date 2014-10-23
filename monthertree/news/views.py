from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
import json

def today(request):
	today_news = [
		{"news": "No news is good news."},
		{"news": "The great use of life is to spend it for something that overlasts it."},
	]
	# scrapy today news from web
	return HttpResponse(toJSON(today_news))

def latest(request):
	latest_news = [
		{"news": "Failure is not  fatal, but failure to change might be."}
	]
	# scrapy latest news from web
	return HttpResponse(toJSON(latest_news))

def toJSON(object):
	"""Dumps the data represented by the object to JSON for wire transfer."""
	return json.dumps(object, ensure_ascii=False)
