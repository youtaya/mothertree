from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.client import Client
from models import Time
import json
import logging

class syncTests(TestCase):
	def test_reset_db(self):
		response = self.client.post(reverse('times:reset'))
		records = Time.objects.all()
		self.assertEqual(len(records), 2)
		self.assertEqual(len(records), 5)
		
	def test_sync_with_user(self):
		python_dict = {
			"username": "temp",
			"records": {
				"handle": "temp",
				"title": "hello, world",
				"content": "test for test",
				"create_date": "2014-4-24",
				"create_time": "20:11:3421",
				"content_type": 1,
				"photo": "",
				"audio": "",
			},
			"host_url": "abc",
		}
		response = self.client.post(reverse('times:sync'),
			#json.dumps(python_dict),
			python_dict,
			content_type="application/xhtml")
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.status_code, 301)

