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
				"date": timezone.now(),
				"time": timezone.now(),
				"ctx": 1,
				"po": "123",
				"ao": "234",
                                "dirty": 1,
                                "deleted": 0,
			},
			{
				"handle": "temp",
				"title": "time",
				"content": "I'm coming again",
				"date": timezone.now(),
				"time": timezone.now(),
				"ctx": 1,
				"po": "123",
				"ao": "",
                                "dirty": 1,
                                "deleted": 0,
			},
		]
		python_dict = {
			"username": "temp",
			"records": json.dumps(json_data, default=default),
		}
		response = self.client.post(reverse('times:sync') 
			,python_dict)
			#content_type="application/json")
		records = Time.objects.all()
                for record in records:
                    self.assertEqual(record.id,0)
		self.assertEqual(len(records), 1)

	def test_share_with_user(self):
		json_data = {
			"handle": "temp",
			"title": "hello, world",
			"content": "test for test",
			"date": timezone.now(),
			"time": timezone.now(),
			"ctx": 1,
			"po": "123",
			"ao": "",
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
