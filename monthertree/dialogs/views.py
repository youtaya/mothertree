from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
import json
import time as _time
from datetime import datetime
from models import Dialog
from django.contrib.auth.models import User
from times.forms import UploadFileForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.utils.encoding import smart_unicode
import logging
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.views import generic
from random import randint

import jpush as jpush
from monthertree.conf import app_key, master_secret

logger = logging.getLogger(__name__)

def safe_attr(obj, attr_name):
	if attr_name in obj:
		return obj[attr_name]
	return None

def jpush_send_message(push_src, push_target, id):
	_jpush = jpush.JPush(app_key, master_secret)
	push = _jpush.create_push()
	push.audience = jpush.audience(
		# push_target may user account or phone number
		jpush.tag(push_target)
	)
	push.message = jpush.message(msg_content=id, extras=str(push_src))
	push.platform = jpush.all_
	push.send()

def pack_dialog_json(item):
	pack_data = {}
	PackDialogData(pack_data, item)

	return pack_data

class PackDialogData(object):
	"""Holds data for user's records.

	This class knows how to serialize itself to JSON.
	"""
	__FIELD_MAP = {
		'handle': 'user',
		'room_name': 'room',
		'link': 'link',
		'content': 'content',
		'create_date': 'date',
		'create_time': 'time',
		'content_type': 'ctx',
		'photo': 'po',
		'audio': 'ao',
		'direct': 'dir',
		'client_id': 'cid'
	}

	def __init__(self, pack_data, dialog_item):

		for obj_name, json_name in self.__FIELD_MAP.items():
			if hasattr(dialog_item, obj_name):
				v = getattr(dialog_item, obj_name)
				if (v != None):
					pack_data[json_name] = smart_unicode(v)
				else:
					pack_data[json_name] = None

		pack_data['sid'] = str(dialog_item.id)
		#pack_data['x'] = high_water_mark

def get_dialog(request):
	username = request.POST.get('username')
	get_id = request.POST.get('id')
	logger.debug("get id: "+ get_id)

	dialog_item = Dialog.objects.get(handle=username, id=int(get_id))
	data = pack_dialog_json(dialog_item)
	return HttpResponse(json.dumps(data,ensure_ascii=False),content_type='application/json')

def process_client_anonymous_share(records_buffer, username):

    jrecord = json.loads(records_buffer)
    logger.debug("jsons list: "+ str(jrecord))
    #select random target handle : not user or user's friends
    totalIds = User.objects.all().count() - 1
    if totalIds <= 1:
        return

    randomId = randint(0, totalIds)
    others = User.objects.get(id=randomId)
    if others.username == username or others.username == 'root':
        randomId = randint(0, totalIds)
        others = User.objects.get(id=randomId)
    target_handle = others.username
    logger.debug('target handle: ' + target_handle)

    record = Dialog(handle=target_handle)

    record.title = safe_attr(jrecord, 'title')

    record.content = safe_attr(jrecord, 'content')
    logger.debug('record context: ' + record.content)
    logger.debug('record username: ' + username)
    record.link = username
    record.create_date = timezone.now()
    record.create_time = timezone.now()
    record.content_type = safe_attr(jrecord, 'ctx')
    record.photo = safe_attr(jrecord, 'po')
    record.audio = safe_attr(jrecord, 'ao')
    record.deleted = (safe_attr(jrecord, 'del') == 'true')

    record.save()
    logger.debug('Saved record: '+record.handle)
    jpush_send_message(username, target_handle, record.id)

def process_client_share(records_buffer, username, target_handle):

    jrecord = json.loads(records_buffer)
    logger.debug("jsons list: "+ str(jrecord))

    record = Dialog(handle=target_handle)

    record.title = safe_attr(jrecord, 'title')

    record.content = safe_attr(jrecord, 'content')
    logger.debug('record username: ' + username)
    record.link = username
    record.create_date = timezone.now()
    record.create_time = timezone.now()
    record.content_type = safe_attr(jrecord, 'ctx')
    record.photo = safe_attr(jrecord, 'po')
    record.audio = safe_attr(jrecord, 'ao')
    record.deleted = (safe_attr(jrecord, 'del') == 'true')

    record.save()
    logger.debug('Saved record: '+record.handle)
    jpush_send_message(username, target_handle, record.id)

def share(request):

    username = request.POST.get('username')
    client_buffer = request.POST.get('records')
    target = request.POST.get('target')
    if target == 'anonymous':
        process_client_anonymous_share(client_buffer, username)
    else:
        process_client_share(client_buffer, username, target)
    return HttpResponse(200)

def resetdb(request):
	records = Dialog.objects.all()
	for record in records:
		record.delete()

	record1 = Dialog(handle='temp',
		content="what's thsis",
		create_date=timezone.now(),
		create_time=timezone.now(),
		content_type=1,
		link="temp",
		deleted=False)
	record1.save()

	record2 = Dialog(handle='temp',
		content="time filping",
		create_date=timezone.now(),
		create_time=timezone.now(),
		content_type=1,
		link="temp",
		deleted=False)
	record2.save()

	return HttpResponse(200)
