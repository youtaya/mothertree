from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from bson.json_util import default, object_hook
import json
import time as _time
from datetime import datetime
from models import Time
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import logging

from django.views import generic

logger = logging.getLogger(__name__)

@login_required
def index(request):
	logger.debug("request: %s" %request.user)
	#latest_time_list = Time.objects.filter(user=request.get('username'))
	latest_time_list = Time.objects.filter(handle='jinxp')
	context = {'latest_time_list': latest_time_list}

	return render(request, 'times/index.html', context)


def list_contains_record(record_list, record):
	if (record is None):
		return False

	record_id = str(record.id)
	for next in record_list:
		if ((next != None) and (next['sid'] == record_id)):
			return True
	return False
	
def safe_attr(obj, attr_name):
	if attr_name in obj:
		return obj[attr_name]
	return None

def process_client_changes(request_url, records_buffer, updated_records):
	logger.debug('* Processing client changes')
	base_url = request_url

	# build an array of generic objects containing contact data,
	# using the Django built-in JSON parser
	logger.debug('Uploaded records buffer: ' + str(records_buffer))
	json_list = json.loads(records_buffer, object_hook=object_hook)
	logger.debug('Client-side updates: ' + str(len(json_list)))

	# keep track of the number of new records the client sent to us,
	# so that we can log it below
	new_record_count = 0

	for jrecord in json_list:
		logger.debug('json record ' + str(jrecord))
		new_record = False
		sid = safe_attr(jrecord, 'sid')
		if(sid != None):
			logger.debug('Updating record: ' + str(sid))
			record = Time.objects.get(id=sid)
		else:
			logger.debug('creating new time record')
			new_record = True
			# todo : need pass user name to handle
			record = Time(handle='temp')

		# if the 'change' for this record is that they were deleted
		# on the client-side, all we want to do is set the deleted
		# flag here, and we're done.
		if(safe_attr(jrecord,'del') == True):
			record.deleted = True
			record.save()
			logger.debug('Deleted record: '+record.handle)
			continue

		record.title = safe_attr(jrecord, 'title')
		logger.debug('record title: ' + record.title)
		record.content = safe_attr(jrecord, 'content')
		record.create_date = safe_attr(jrecord, 'date')
		record.create_time = safe_attr(jrecord, 'time')
		#record.create_date = timezone.now()
		#record.create_time = timezone.now()
		record.content_type = safe_attr(jrecord, 'ctx')
		record.photo = safe_attr(jrecord, 'po')
		record.audio = safe_attr(jrecord, 'ao')
		record.deleted = (safe_attr(jrecord, 'del') == 'true')
		if(new_record):
			# new record - add them to db ...
			new_record_count = new_record_count + 1
			record.handle = 'temp'
			logger.debug('Created new record handle: '+ record.handle)
		record.save()
		logger.debug('Saved record: '+record.handle)

		# we don't save off the client_id value (thus we add it after
		# the "save"), but we want it to be in the JSON object we
		# serialize out, so that the client can match this contact
		# up with the client version
		client_id = safe_attr('jrecord', 'cid')

		# create a high-water-mark for sync-state from the 'updated' time
		# for this record, so we return the corrent value to the client.
		high_water = str(long(_time.mktime(record.updated.utctimetuple())) + 1)

		# add new records to our updated_records, so that we return them
		# to the client (so the client gets the serverId for the 
		# added record)
		if (new_record):
			UpdatedRecordData(updated_records, record.handle, client_id, base_url,
				high_water)

	logger.debug('Client-side adds: '+str(new_record_count))



def get_updated_records(request_url, client_state, updated_records):
	logger.debug('* Processing server changes')
	timestamp = None

	base_url = request_url

	# the client sends the last high-water-mark that they sucessfully
	# sync'd to in the syncstate parameter. it's opaque to them, but
	# its actually a seconds-in-unix-epoch timestamp that we use
	# as a baseline.
	if client_state:
		logger.debug('Client sync state: '+client_state)
		timestamp = datetime.utcformattimestamp(float(client_state))

	# keep track of the update/delete counts, so we can log in
	# below. Makes debugging easier...
	update_count = 0
	delete_count = 0

	records = Time.objects.all()
	if records:
		# find the high-water mark for the most recently updated friend.
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

		# Now build the updated_records containing all the friends that have been
		# changed since the last sync
		for record in records:
			# if our list of records we're returning already contains this
			# contact (for example, it's a record just uploaded from the client)
			# then don't bother processing it any further...
			if (list_contains_record(updated_records, record)):
				continue

			handle = record.handle

			if timestamp is None or record.updated > timestamp:
				if record.deleted == True:
					delete_count = delete_count + 1
					DeletedRecordData(updated_records, handle, high_water_mark)
				else:
					update_count = update_count + 1
					UpdatedRecordData(updated_records, handle, None, base_url, high_water_mark)

	logger.debug('Server-side updates: '+str(update_count))
	logger.debug('Server-side deletes: '+str(delete_count))

def sync(request):

	# get user name: request.get('username')
	username = 'temp'
	# upload client dirty records
	updated_records = []
	if request.method == 'POST':
		logger.debug("request POST: "+str(request.POST))
	else:
		logger.debug("request GET: "+str(request.GET))
	client_buffer = request.POST.get('records')
	request_url = request.POST.get('host_url')

	if((client_buffer != None) and (client_buffer != '')):
		process_client_changes(request_url, client_buffer, updated_records)
	
	# add any records on the server-side
	client_state = request.POST.get('syncstate')
	get_updated_records(request_url, client_state, updated_records)

	# update latest records
	#HttpResponse.status(200)
	return HttpResponse(toJSON(updated_records))

def resetdb(request):
	records = Time.objects.all()
	for record in records:
		record.delete()

	record1 = Time(handle='temp',
		title="test1",
		content="what's thsis",
		create_date=timezone.now(),
		create_time=timezone.now(),
		content_type=1,
		status="now ok",
		deleted='False')
	record1.save()

	record2 = Time(handle='temp',
		title="test2",
		content="time filping",
		create_date=timezone.now(),
		create_time=timezone.now(),
		content_type=1,
		status="we are still here",
		deleted='False')
	record2.save()

	return HttpResponse(200)

def process_client_share(records_buffer, target_handle):
	record = Time(handle='abc')
	jrecord = json.loads(records_buffer, object_hook=object_hook)
	logger.debug("jsons list: "+ str(jrecord))

	record.title = safe_attr(jrecord, 'title')
	
	record.content = safe_attr(jrecord, 'content')
	logger.debug('record context: ' + record.content)
	record.create_date = timezone.now()
	record.create_time = timezone.now()
	record.content_type = safe_attr(jrecord, 'ctx')
	record.photo = safe_attr(jrecord, 'po')
	record.audio = safe_attr(jrecord, 'ao')
	record.deleted = (safe_attr(jrecord, 'del') == 'true')

	record.save()
	logger.debug('Saved record: '+record.handle)

def share(request):
	username = 'temp'
	client_buffer = request.POST.get('records')
	target = request.POST.get('target')
	process_client_share(client_buffer, target)
	return HttpResponse(200)

def toJSON(object):
	"""Dumps the data represented by the object to JSON for wire transfer."""
	return json.dumps(object, default=default)

class UpdatedRecordData(object):
	"""Holds data for user's records.

	This class knows how to serialize itself to JSON.
	"""
	__FIELD_MAP = {
		'handle': 'user',
		'title': 'title',
		'content': 'ct',
		'create_date': 'date',
		'create_time': 'time',
		'content_type': 'ctx',
		'photo': 'po',
		'audio': 'ao',
		'status': 'status',
		'client_id': 'cid'
	}

	def __init__(self, record_list, username, client_id, host_url, high_water_mark):
		obj = Time.objects.get(handle=username)
		record = {}
		for obj_name, json_name in self.__FIELD_MAP.items():
			if hasattr(obj, obj_name):
				v = getattr(obj, obj_name)
				if (v != None):
					record[json_name] = str(v)
				else:
					record[json_name] = None

		record['sid'] = str(obj.id)
		record['x'] = high_water_mark
		if (client_id != None):
			record['cid'] = str(client_id)
		record_list.append(record)

class DeletedRecordData(object):
	def __init__(self, record_list, username, high_water_mark):
		obj = Time.objects.get(handle=username)
		record = {}
		record['del'] = 'true'
		record['cid'] = str(obj.id)
		record['x'] = high_water_mark
		record_list.append(record)		