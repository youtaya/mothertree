from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.client import Client
from models import Dialog
from django.utils import timezone
import json
import logging

class shareTests(TestCase):

	def setUp(self):
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

	def test_share_with_user(self):
		json_data = {
			"handle": "temp",
			"sender": "temp",
			"link": "abc",
			"direct": 1,
			"content": "test for test",
			"date": "2014-05-15",
			"time": "2014-05-15 23:12:34",
			"ctx": 1,
			"po": "123",
			"ao": "",
			"cid": 6,
		}

		python_dict = {
			"username": "temp",
			"records": json.dumps(json_data, ensure_ascii=False),
			"target": "abc"
		}

		response = self.client.post(reverse('dialogs:share'),python_dict)
		record = Dialog.objects.get(handle='abc')
		self.assertEqual(record.link, "temp")
		self.assertEqual(response.status_code, 200)

	def test_anonyous_share_with_user(self):
		json_data = {
			"handle": "temp",
			"link": "temp",
			"direct": 2,
			"content": "test for test",
			"date": "2014-05-15",
			"time": "2014-05-15 23:12:34",
			"ctx": 1,
			"po": "123",
			"ao": "",
			"cid": 6,
		}

		python_dict = {
			"username": "temp",
			"records": json.dumps(json_data, ensure_ascii=False),
			"target": "anonymous"
		}

		response = self.client.post(reverse('dialogs:share'),python_dict)
		self.assertEqual(response.status_code, 200)

	def test_get_dialog(self):

		python_dict = {
			"username": "temp",
			"id": 1,
		}
		response = self.client.post(reverse('dialogs:getdialog'),python_dict)
		self.assertEqual(response.content, "ok")
