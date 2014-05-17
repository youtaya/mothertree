from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.client import Client
from models import Time
from django.utils import timezone
from bson.json_util import default, object_hook
import json
import logging

class syncTests(TestCase):
	def test_reset_db(self):
		response = self.client.post(reverse('times:reset'))
		records = Time.objects.all()
		self.assertEqual(len(records), 2)

	def test_sync_with_user(self):
		json_data = [
			{
				"handle": "temp",
				"title": "hello, world",
				"content": "test for test",
				"date": "2014/05/16",
				"time": "2014/05/16 21:22:31",
				"ctx": 1,
				"po": "123",
				"ao": "",
				"cid": 5, 
			},
			{
				"handle": "temp",
				"title": "next, step",
				"content": "share friend",
				"date": "2014/05/16",
				"time": "2014/05/16 22:29:11",
				"ctx": 1,
				"po": "",
				"ao": "234",
				"cid": 6, 
			},			
		]
		python_dict = {
			"username": "temp",
			"records": json.dumps(json_data, default=default),
		}
		response = self.client.post(reverse('times:sync') 
			,python_dict)
			#content_type="application/json")
		self.assertEqual(response.content, "ok")
		records = Time.objects.all()
		self.assertEqual(len(records), 1)

	def test_share_with_user(self):
		json_data = {
			"handle": "temp",
			"title": "hello, world",
			"content": "test for test",
			"date": "2014/05/15",
			"time": "2014/05/15 23:12:34",
			"ctx": 1,
			"po": "123",
			"ao": "",
			"cid": 6,
		}
		
		python_dict = {
			"username": "temp",
			"records": json.dumps(json_data, default=default),
			"target": "abc"
		}

		response = self.client.post(reverse('times:share'),python_dict)
		record = Time.objects.get(handle='abc')
		self.assertEqual(record.content, "hello,world")
		self.assertEqual(len(record), 2)
		self.assertEqual(response.status_code, 200)