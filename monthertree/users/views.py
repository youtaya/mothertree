# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
import json
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
			return HttpResponse(json.dumps(data,ensure_ascii=False),content_type='application/json')

		if password!=confirmpass:
			data['status']=10
			data['error']='password not correct'
			return HttpResponse(json.dumps(data,ensure_ascii=False),content_type='application/json')

		logger.debug("[Register]:"+str(user_name)+" / "+str(password))
		try:
			check_user = User.objects.get(username=user_name)
			data['status']=16
			data['error']='username already used'
			return HttpResponse(json.dumps(data,ensure_ascii=False),content_type='application/json')
		except ObjectDoesNotExist:
			user=User(username=user_name,password=password,is_staff=False,is_active=True,is_superuser=False)
			user.save()
			data['status']=0
			return HttpResponse(json.dumps(data,ensure_ascii=False),content_type='application/json')

	data['status']=404
	return HttpResponse(json.dumps(data,ensure_ascii=False),content_type='application/json')


def login(request):
	data={}

	if request.method == 'POST':
		logger.debug(str(request.POST))
		user_name = request.POST.get('username' )
		password = request.POST.get('password')
		# password=make_password(password)
		logger.debug("[Login]:"+str(user_name)+" / "+str(password))

		user = User.objects.filter(username = user_name,password = password)

		if user:
			logger.debug("user is exist!!")
			data['status']=0
			return HttpResponse(json.dumps(data,ensure_ascii=False),content_type='application/json')

	data['status']=503
	return HttpResponse(json.dumps(data,ensure_ascii=False),content_type='application/json')
