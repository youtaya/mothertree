from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.encoding import smart_unicode
from django.core.exceptions import ObjectDoesNotExist
from friends.models import Friend
from users.models import UserInfo
from utils.packed_json import toJSON
from utils.packed_jpush import jpush_send_message
import json
import time as _time
from datetime import datetime
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

def recommend(request):
	recommend_friends = {}
	friend_list = []
	friends = User.objects.all()
	for friend in friends:
		if(friend.username == "root"):
			continue
		logger.debug("friend is : %s" %friend.username)
		friend_info = UserInfo.objects.get(user=friend)
		recommend = {}
		recommend['u'] = friend.username
		recommend['a'] = friend_info.avatar_url()

		friend_list.append(recommend)

	recommend_friends['recommend'] = friend_list

	return HttpResponse(toJSON(recommend_friends))

def add_friend(request):
	data = {}

	if request.method == 'POST':
		logger.debug(str(request.POST))
		user_name = request.POST.get('username')
		logger.debug("src user name : "+user_name)
		try:
			src_user = User.objects.get(username = user_name)
		except ObjectDoesNotExist:
			data['status']=34
			return HttpResponse(toJSON(data))

		target_user=request.POST.get('target_user')
		# comment: for identify who that add
		# comment = request.POST.get('comment')

		try:
			add_user = User.objects.get(username=target_user)

			try:
				check_friend = Friend.objects.get(handle=src_user, friend=add_user)
				logger.debug("friend already add, skip it")
			except ObjectDoesNotExist:
				wait_friend = Friend.objects.create(handle = src_user, friend=add_user)
				wait_friend.verify_status = 2
				wait_friend.save()

				push_data = {}
				push_data = wait_friend.get_friend_info()
				logger.debug("friend info : "+str(push_data))
				jpush_send_message(toJSON(push_data), target_user, 1002)

			data['status']=0
			return HttpResponse(toJSON(data))
		except ObjectDoesNotExist:
			data['status']=28
			return HttpResponse(toJSON(data))

def accept_friend(request):
	data = {}

	if request.method == 'POST':
		logger.debug(str(request.POST))

		user_name = request.POST.get('username')
		# 1: agree, 0: disagree
		nok = request.POST.get('nok')
		try:
			src_user = User.objects.get(username = user_name)

		except ObjectDoesNotExist:
			data['status']=34
			return HttpResponse(toJSON(data))

		target_user=request.POST.get('target_user')

		try:
			target = User.objects.get(username=target_user)
			origin = User.objects.get(username=user_name)
			friend = Friend.objects.get(handle=target,friend=origin)
			if(nok is 1):
				# change friend verify status
				friend.verify_status = 1
				friend.save()
			else:
				# disagree to add, so delete it
				friend.delete()

			push_data = {}
			push_data['user_name'] = user_name
			jpush_send_message(toJSON(push_data), target_user, 1003)

			data['status']=0
			return HttpResponse(toJSON(data))
		except ObjectDoesNotExist:
			data['status']=28
			return HttpResponse(toJSON(data))

def update_friend(request):
	data = {}

	if request.method == 'POST':
		logger.debug(str(request.POST))

		user_name = request.POST.get('username')
		name_comment = request.POST.get('name_comment')
		descrip = request.POST.get('description')

		target_user=request.POST.get('target_user')

		try:
			src_user = User.objects.get(username = user_name)
			logger.debug("friend description is "+descrip)
			update_user = User.objects.get(username=target_user)
			my_friend = Friend.objects.get(handle=src_user,friend=update_user)

			# set breakpoint to trace
			#import pdb; pdb.set_trace()
			my_friend.name_comment = name_comment
			my_friend.description = descrip
			my_friend.save()

			data['status']=0
			return HttpResponse(toJSON(data))
		except ObjectDoesNotExist:
			data['status']=28
			return HttpResponse(toJSON(data))



def list_contains_record(record_list, record):
	if (record is None):
		return False

	record_id = record.id
	for next in record_list:
		if ((next != None) and (next['sid'] == record_id)):
			return True
	return False

def safe_attr(obj, attr_name):
	if attr_name in obj:
		return obj[attr_name]
	return None

def process_client_changes(src_user, friends_buffer):
	logger.debug('* Processing client changes')

	# build an array of generic objects containing contact data,
	# using the Django built-in JSON parser
	logger.debug('Uploaded friends buffer: ' + smart_unicode(friends_buffer))
	json_list = json.loads(friends_buffer)
	logger.debug('Client-side updates: ' + str(len(json_list)))

	for jrecord in json_list:
		logger.debug('json record ' + str(jrecord))
		new_record = False
		sid = safe_attr(jrecord, 'sid')
		if(sid != None):
			logger.debug('Updating record: ' + str(sid))
			record = Friend.objects.get(id=sid)

		# if the 'change' for this record is that they were deleted
		# on the client-side, all we want to do is set the deleted
		# flag here, and we're done.
		if(safe_attr(jrecord,'d') == 1):
			record.deleted = True
			record.save()
			logger.debug('Deleted record: '+record.handle)


def get_updated_friends(src_user, client_state, updated_friends):
	logger.debug('* Processing server changes')
	timestamp = None

	# the client sends the last high-water-mark that they sucessfully
	# sync'd to in the syncstate parameter. it's opaque to them, but
	# its actually a seconds-in-unix-epoch timestamp that we use
	# as a baseline.
	if client_state:
		logger.debug('Client sync state: '+client_state)
		timestamp = datetime.utcformattimestamp(long(client_state))

	# keep track of the update/delete counts, so we can log in
	# below. Makes debugging easier...
	update_count = 0
	delete_count = 0

	records = Friend.objects.filter(handle=src_user)
	if records:
		# find the high-water mark for the most recently updated record.
		# we'll return this as the syncstate (x) value for all the friends
		# we return from this function.
		high_water_date = datetime.min
		for record in records:
			result = record.updated.replace(microsecond=0, tzinfo=None)
			logger.debug("record updated: "+str(result))
			logger.debug("high water date: "+str(high_water_date))
			if (result > high_water_date):
				high_water_date = result
		high_water_mark = str(long(_time.mktime(high_water_date.utctimetuple())) + 1)
		logger.debug('New sync state: '+high_water_mark)

		# Now build the updated_friends containing all the friends that have been
		# changed since the last sync
		for record in records:
			# if our list of records we're returning already contains this
			# record (for example, it's a record just uploaded from the client)
			# then don't bother processing it any further...
			if (list_contains_record(updated_friends, record)):
				continue

			friend_name = record.friend.username
			friend = User.objects.get(username=friend_name)
			logger.debug("record updated: "+str(record.updated))
			logger.debug("timestamp: "+str(timestamp))
			if timestamp is None or record.updated > timestamp:
				if record.deleted == True:
					delete_count = delete_count + 1
					DeletedRecordData(updated_friends, src_user, friend, high_water_mark)
					record.delete()
				else:
					update_count = update_count + 1
					UpdatedRecordData(updated_friends, src_user, friend, None, high_water_mark)

	logger.debug('Server-side updates: '+str(update_count))
	logger.debug('Server-side deletes: '+str(delete_count))

def sync_friend(request):

	user_name = request.POST.get('username')
	# upload client dirty friends
	updated_friends = []
	result_friends = {}
	if request.method == 'POST':
		logger.debug("request POST: "+str(request.POST))
	else:
		logger.debug("request GET: "+str(request.GET))
	client_buffer = request.POST.get('friends')

	src_user = User.objects.get(username = user_name)

	if((client_buffer != None) and (client_buffer != '')):
		process_client_changes(src_user, client_buffer)

	# add any friends on the server-side
	client_state = request.POST.get('syncstate')
	get_updated_friends(src_user, client_state, updated_friends)

	result_friends['friends'] = updated_friends
	logger.debug("update friends are : "+toJSON(result_friends))
	# update latest friends
	return HttpResponse(toJSON(result_friends))


class UpdatedRecordData(object):
	"""Holds data for user's records.

	This class knows how to serialize itself to JSON.
	"""
	__FIELD_MAP = {
		'handle': 'h',
		'friend': 'f',
		'avatar': 'a',
		'description': 'des',
		'deleted': 'd',
		'client_id': 'cid'
	}

	def __init__(self, record_list, src_user, friend_user, client_id, high_water_mark):
		obj = Friend.objects.get(handle = src_user, friend=friend_user)

		record = {}
		data = obj.get_friend_info()
		record['f'] = data['friend']
		record['a'] = data['avatar']

		record['sid'] = obj.id
		record['x'] = high_water_mark
		if (client_id != None):
			logger.debug("mark client id: "+str(client_id))
			record['cid'] = client_id
		record_list.append(record)

class DeletedRecordData(object):
	def __init__(self, record_list, src_user, friend_user, high_water_mark):
		obj = Friend.objects.get(handle = src_user, friend=friend_user)
		record = {}
		record['d'] = 1
		record['sid'] = obj.id
		record['x'] = high_water_mark
		record_list.append(record)
