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

logger = logging.getLogger(__name__)

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

def share(request):

    username = request.POST.get('username')
    client_buffer = request.POST.get('records')
    target = request.POST.get('target')
    if target == 'anonymous':
        process_client_anonymous_share(client_buffer, username)
    else:
        process_client_share(client_buffer, username, target)
    return HttpResponse(200)
