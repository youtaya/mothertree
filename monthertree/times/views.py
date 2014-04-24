from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
import json
import time as _time
from datetime import datetime
from models import Time
from django.contrib.auth.decorators import login_required
import logging

from django.views import generic

#logger = logging.getLogger(__name__)

@login_required
def index(request):
	logging.info("request: %s" %request.user)
	#latest_time_list = Time.objects.filter(user=request.get('username'))
	latest_time_list = Time.objects.filter(handle='jinxp')
	context = {'latest_time_list': latest_time_list}

	return render(request, 'times/index.html', context)


def list_contains_record(record_list, record):
	if (record is None):
		return False

	record_id = str(record.key().id())
	for next in record_list:
		if ((next != None) and (next['sid'] == record_id)):
			return True
	return False
	
def safe_attr(obj, attr_name):
	if attr_name in obj:
		return obj[attr_name]
	return None

def process_client_changes(request_url, records_buffer, updated_records):
	logging.info('* Processing client changes')
	base_url = request_url

	# build an array of generic objects containing contact data,
	# using the Django built-in JSON parser
	logging.info('Uploaded records buffer: ' + records_buffer)
	json_list = json.loads(records_buffer)
	logging.info('Client-side updates: ' + str(len(json_list)))

	# keep track of the number of new records the client sent to us,
	# so that we can log it below
	new_record_count = 0

	for jrecord in json_list:
		new_record = False
		sid = safe_attr(jrecord, 'sid')
		if(sid != None):
			logging.info('Updating record: ' + str(sid))
			record = Time.objects.get(id=sid)
		else:
			logging.info('creating new time record')
			new_record = True
			# todo : need pass user name to handle
			record = Time(handle='temp')

		# if the 'change' for this record is that they were deleted
		# on the client-side, all we want to do is set the deleted
		# flag here, and we're done.
		if(safe_attr(jrecord,'del') == True):
			record.deleted = True
			record.save()
			logging.info('Deleted record: '+record.handle)
			continue

		record.title = safe_attr(jrecord, 'title')
		record.context = safe_attr(jrecord, 'ct')
		record.create_date = safe_attr(jrecord, 'date')
		record.create_time = safe_attr(jrecord, 'time')
		record.content_type = safe_attr(jrecord, 'ctx')
		record.photo = safe_attr(jrecord, 'po')
		record.audio = safe_attr(jrecord, 'ao')
		record.deleted = (safe_attr(jrecord, 'del') == 'true')
		if(new_record):
			# new record - add them to db ...
			new_record_count = new_record_count + 1
			record.handle = 'temp'
			logging.info('Created new record handle: '+ record.handle)
		record.save()
		logging.info('Saved record: '+record.handle)

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

	logging.info('Client-side adds: '+str(new_record_count))



def get_updated_records(request_url, client_state, updated_records):
	logging.info('* Processing server changes')
	timestamp = None

	base_url = request_url

	# the client sends the last high-water-mark that they sucessfully
	# sync'd to in the syncstate parameter. it's opaque to them, but
	# its actually a seconds-in-unix-epoch timestamp that we use
	# as a baseline.
	if client_state:
		logging.info('Client sync state: '+client_state)
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
			if (record.updated > high_water_date):
				high_water_date = record.updated
		high_water_mark = str(long(_time.mktime(high_water_date.utctimetuple())) + 1)
		logging.info('New sync state: '+high_water_mark)

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

	logging.info('Server-side updates: '+str(update_count))
	logging.info('Server-side deletes: '+str(delete_count))

def sync(request):

	# get user name: request.get('username')
	username = 'temp'
	# upload client dirty records
	updated_records = []
	logging.info("request: "+str(request.POST.get('username')))
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

def toJSON(object):
	"""Dumps the data represented by the object to JSON for wire transfer."""
	return json.dumps(object)

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
		obj = time.objects.get(handle=username)
		record = {}
		for obj_name, json_name in self.__FIELD_MAP.items():
			if hasattr(obj, obj_name):
				v = getattr(obj, obj_name)
				if (v != None):
					record[json_name] = str(v)
				else:
					record[json_name] = None

		record['sid'] = str(obj.key().id())
		record['x'] = high_water_mark
		if (client_id != None):
			record['cid'] = str(client_id)
		record_list.append(record)

class DeletedRecordData(object):
	def __init__(self, record_list, username, high_water_mark):
		obj = Time.objects.get(handle=username)
		record = {}
		record['del'] = 'true'
		record['cid'] = str(obj.key().id())
		record['x'] = high_water_mark
		record_list.append(record)		