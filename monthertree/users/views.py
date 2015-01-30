# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
import json
from utils.packed_json import toJSON
import time
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from users.models import UserInfo
from django.core.urlresolvers import reverse
import logging

logger = logging.getLogger(__name__)

def signup(request):
	data={}

	if request.method=='POST':
		logger.debug(str(request.POST))

		try:
			user_name=request.POST.get('username')
			password=request.POST.get('password')
			confirmpass=request.POST.get('password')
		except KeyError:
			data['status']=14
			data['error']='missing items'
			return HttpResponse(toJSON(data))

		if password!=confirmpass:
			data['status']=10
			data['error']='password not correct'
			return HttpResponse(toJSON(data))

		logger.debug("[Register]:"+str(user_name)+" / "+str(password))
		try:
			check_user = User.objects.get(username=user_name)
			data['status']=16
			data['error']='username already used'
			return HttpResponse(toJSON(data))
		except ObjectDoesNotExist:
			user=User(username=user_name,password=password,is_staff=False,is_active=True,is_superuser=False)
			user.save()
			data['status']=0
			return HttpResponse(toJSON(data))

	data['status']=404
	return HttpResponse(toJSON(data))


def login(request):
	data={}

	if request.method == 'POST':
		logger.debug(str(request.POST))
		user_name = request.POST.get('username')
		password = request.POST.get('password')
		# password=make_password(password)
		logger.debug("[Login]:"+str(user_name)+" / "+str(password))

		user = User.objects.filter(username = user_name,password = password)

		if user:
			logger.debug("user is exist!!")
			data['status']=0
			return HttpResponse(toJSON(data))

	data['status']=503
	return HttpResponse(toJSON(data))

def search_people(request):
	data = {}

	if request.method == 'POST':
		logger.debug(str(request.POST))

		user_name = request.POST.get('username')
		search_friend = request.POST.get('search_str')

		try:
			client_user = User.objects.get(username = user_name)
			result = User.objects.filter(username=search_friend)

			record_list = []
			for friend in result:
				get_friend = UserInfo.objects.get(user=friend)
				record = {}
				record['nickname'] = smart_unicode(get_friend.nickname)
				# TODO: fix it
				record['avatar_url'] = ""
				record['mobile'] = smart_unicode(friend.username)

				record_list.append(record)

			data['status'] = 0
			data['friends'] = record_list
			return HttpResponse(toJSON(data))
		except ObjectDoesNotExist:
			data['status']=0
			data['friends']= []
			return HttpResponse(toJSON(data))

		data['status']=55
		return HttpResponse(toJSON(data))
