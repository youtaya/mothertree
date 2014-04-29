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
				#"date": "2014-4-25",
				#"time": "2014-4-25 08:22:34",
				"ctx": 1,
				"po": "123",
				"ao": "",
			},
		]
		python_dict = {
			"username": "temp",
			"records": json.dumps(json_data, default=default),
			"host_url": "abc"
		}
		response = self.client.post(reverse('times:sync') 
			,python_dict)
			#content_type="application/json")
		records = Time.objects.all()
		self.assertEqual(len(records), 1)
		self.assertEqual(response.status_code, 200)
		

