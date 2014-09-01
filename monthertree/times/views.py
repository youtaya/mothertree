from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from bson.json_util import default, object_hook
import json
import time as _time
from datetime import datetime
from models import Time
from django.contrib.auth.models import User
from forms import UploadFileForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.utils.encoding import smart_unicode
import logging
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.views import generic
from random import randint

logger = logging.getLogger(__name__)

@login_required
def index(request):
	logger.debug("request: %s" %request.user)
	#latest_time_list = Time.objects.filter(user=request.get('username'))
	latest_time_list = Time.objects.filter(handle='temp')
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

def process_client_changes(request_url, username, records_buffer, updated_records):
	logger.debug('* Processing client changes')
	base_url = request_url

	# build an array of generic objects containing contact data,
	# using the Django built-in JSON parser
	logger.debug('Uploaded records buffer: ' + smart_unicode(records_buffer))
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
			record = Time(handle=username)

		# if the 'change' for this record is that they were deleted
		# on the client-side, all we want to do is set the deleted
		# flag here, and we're done.
		if(safe_attr(jrecord,'del') == True):
			record.deleted = True
			record.save()
			logger.debug('Deleted record: '+record.handle)
			continue

		if(None != safe_attr(jrecord, 'link')):
			record.link = safe_attr(jrecord, 'link')
		record.title = safe_attr(jrecord, 'title')
		logger.debug('record title: ' + str(record.title))
		record.content = safe_attr(jrecord, 'content')
		record.create_date = safe_attr(jrecord, 'date')
		record.create_time = safe_attr(jrecord, 'time')
		#record.create_date = timezone.now()
		#record.create_time = timezone.now()
		record.content_type = safe_attr(jrecord, 'ctx')
		record.photo = safe_attr(jrecord, 'po')
		record.audio = safe_attr(jrecord, 'ao')
		record.tag = safe_attr(jrecord, 'tag')
		record.deleted = (safe_attr(jrecord, 'del') == 'true')
		if(new_record):
			# new record - add them to db ...
			new_record_count = new_record_count + 1
			#record.handle = 'temp'
			logger.debug('Created new record handle: '+ record.handle)
		record.save()
		logger.debug('Saved record: '+record.handle)

		# we don't save off the client_id value (thus we add it after
		# the "save"), but we want it to be in the JSON object we
		# serialize out, so that the client can match this contact
		# up with the client version
		client_id = safe_attr(jrecord, 'cid')

		mark_time = record.create_time
		logger.debug('record time: ' + mark_time)

		
		# create a high-water-mark for sync-state from the 'updated' time
		# for this record, so we return the corrent value to the client.
		high_water = str(long(_time.mktime(record.updated.utctimetuple())) + 1)

		# add new records to our updated_records, so that we return them
		# to the client (so the client gets the serverId for the 
		# added record)
		if (new_record):
			UpdatedRecordData(updated_records, record.handle, client_id, mark_time,
				base_url, high_water)

	logger.debug('Client-side adds: '+str(new_record_count))



def get_updated_records(request_url, username, client_state, updated_records):
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

	records = Time.objects.filter(handle=username)
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

		# Now build the updated_records containing all the friends that have been
		# changed since the last sync
		for record in records:
			# if our list of records we're returning already contains this
			# record (for example, it's a record just uploaded from the client)
			# then don't bother processing it any further...
			if (list_contains_record(updated_records, record)):
				continue

			handle = record.handle
			create_time = record.create_time
			logger.debug("record updated: "+str(record.updated))
			logger.debug("timestamp: "+str(timestamp))
			if timestamp is None or record.updated > timestamp:
				if record.deleted == True:
					delete_count = delete_count + 1
					DeletedRecordData(updated_records, handle, create_time, high_water_mark)
				else:
					update_count = update_count + 1
					UpdatedRecordData(updated_records, handle, None, create_time, base_url, high_water_mark)

	logger.debug('Server-side updates: '+str(update_count))
	logger.debug('Server-side deletes: '+str(delete_count))

def sync(request):

	username = request.POST.get('username')
	# upload client dirty records
	updated_records = []
	if request.method == 'POST':
		logger.debug("request POST: "+str(request.POST))
	else:
		logger.debug("request GET: "+str(request.GET))
	client_buffer = request.POST.get('records')
	request_url = request.POST.get('host_url')

	if((client_buffer != None) and (client_buffer != '')):
		process_client_changes(request_url, username, client_buffer, updated_records)
	


	# add any records on the server-side
	client_state = request.POST.get('syncstate')
	get_updated_records(request_url, username, client_state, updated_records)

	logger.debug("update records are : "+toJSON(updated_records))
	# update latest records
	#HttpResponse.status(200)
	return HttpResponse(toJSON(updated_records))

def addrecord(request):
	# for test
	record3 = Time(handle='jinxp',
		title="test1",
		content="what's thsis",
		create_date=timezone.now(),
		create_time=timezone.now(),
		content_type=1,
		link="jinxp",
		deleted=False)
	record3.save()

	return HttpResponse(200)


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
		link="temp",
		deleted=False)
	record1.save()

	record2 = Time(handle='temp',
		title="test2",
		content="time filping",
		create_date=timezone.now(),
		create_time=timezone.now(),
		content_type=1,
		link="temp",
		deleted=False)
	record2.save()

	return HttpResponse(200)

def process_client_anonymous_share(records_buffer, username):
	
	jrecord = json.loads(records_buffer, object_hook=object_hook)
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

	record = Time(handle=target_handle)
	
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
	record.tag = safe_attr(jrecord, 'tag')
	record.deleted = (safe_attr(jrecord, 'del') == 'true')

	record.save()
	logger.debug('Saved record: '+record.handle)


def process_client_share(records_buffer, username, target_handle):
	
	jrecord = json.loads(records_buffer, object_hook=object_hook)
	logger.debug("jsons list: "+ str(jrecord))

	record = Time(handle=target_handle)
	
	record.title = safe_attr(jrecord, 'title')
	
	record.content = safe_attr(jrecord, 'content')
	logger.debug('record username: ' + username)
	record.link = username 
	record.create_date = timezone.now()
	record.create_time = timezone.now()
	record.content_type = safe_attr(jrecord, 'ctx')
	record.photo = safe_attr(jrecord, 'po')
	record.audio = safe_attr(jrecord, 'ao')
	if safe_attr(jrecord, 'tag') != None:
		record.tag = safe_attr(jrecord, 'tag')
	record.deleted = (safe_attr(jrecord, 'del') == 'true')

	record.save()
	logger.debug('Saved record: '+record.handle)

def share(request):

	username = request.POST.get('username')
	client_buffer = request.POST.get('records')
	target = request.POST.get('target')
	if target == 'anonymous':
		process_client_anonymous_share(client_buffer, username)
	else:
		process_client_share(client_buffer, username, target)
	return HttpResponse(200)

@csrf_exempt
def photo(request):
	#get image from client
	#save image to media folder
	if request.method == "POST":
		form = UploadFileForm(request.POST, request.FILES)
		logger.debug("[photo]request POST form: "+ str(request.POST))
		if form.is_valid() and form.is_multipart():
			logger.debug("[photo]upload image: "+str(request.FILES))
			save_file(request.FILES['image'])
			return HttpResponse(200)
		else:
			return HttpResponse('invalid image')
	
	if request.method == "GET":
		return render(request, 'times/photo.html')
	
def save_file(file, path=''):
	
	filename = file._get_name()
	logger.debug("[photo]save image: "+filename)

	fd = open('%s/%s' % (settings.MEDIA_ROOT , str(path)+str(filename)), 'wb')
	for chunk in file.chunks():
		fd.write(chunk)
	fd.close()

def photoView(request, image_name):
    """
    Processes request to view photo. 
    It just returns the raw image itself.
    """
    logger.debug("iamge name : "+str(image_name))
    if(image_name != None):
		image_data = open('%s/%s' % (settings.MEDIA_ROOT , str(image_name)), "rb").read()
		return HttpResponse(image_data, content_type="image/png")

def photoView2(request):
    """
    Processes request to view photo. 
    It just returns the raw image itself.
    """

    image_data2 = open('%s/%s' % (settings.MEDIA_ROOT , "20140810231230"), "rb").read()
    return HttpResponse(image_data2, content_type="image/png")

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
		'content': 'content',
		'create_date': 'date',
		'create_time': 'time',
		'content_type': 'ctx',
		'photo': 'po',
		'audio': 'ao',
		'tag': 'tag',
		'link': 'link',
		'client_id': 'cid'
	}

	def __init__(self, record_list, username, client_id, mark_time, host_url, high_water_mark):
		logger.debug("mark create time: "+mark_time)
		obj = Time.objects.get(handle=username, create_time=mark_time)

		record = {}
		for obj_name, json_name in self.__FIELD_MAP.items():
			if hasattr(obj, obj_name):
				v = getattr(obj, obj_name)
				if (v != None):
					record[json_name] = smart_unicode(v)
				else:
					record[json_name] = None

		record['sid'] = str(obj.id)
		record['x'] = high_water_mark
		logger.debug("mark client id: "+str(client_id))
		if (client_id != None):
			record['cid'] = client_id
		record_list.append(record)

class DeletedRecordData(object):
	def __init__(self, record_list, username, mark_time, high_water_mark):
		#allObjs = Time.objects.filter(handle=username)
		obj = Time.objects.get(handle=username, create_time=mark_time)
		record = {}
		record['del'] = 'true'
		record['sid'] = obj.id
		record['x'] = high_water_mark
		record_list.append(record)		
