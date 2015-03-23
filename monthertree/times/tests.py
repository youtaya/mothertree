from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.client import Client
from models import Time
from django.utils import timezone
import json
import logging
from django.contrib.auth.models import User

class syncTests(TestCase):
	def setUp(self):
		user1 = User.objects.create(username='temp')
		user2 = User.objects.create(username='abc')
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

	def test_reset_db(self):
		response = self.client.post(reverse('times:reset'))
		records = Time.objects.all()
		self.assertEqual(len(records), 2)

	def test_sync_with_user(self):
		json_data = [
			{
				"handle": "temp",
				"link": "temp",
				"title": "hello, world",
				"content": "test for test",
				"date": "2014-05-16",
				"time": "2014-05-16 21:22:31",
				"ctx": 1,
				"po": "123",
				"ao": "",
				"cid": 5,
				"dirty": 'true',
				"deleted": 'false',
			},
			{
				"handle": "temp",
				"link": "temp",
				"title": "next, step",
				"content": "share friend",
				"date": "2014-05-16",
				"time": "2014-05-16 22:29:11",
				"ctx": 1,
				"po": "",
				"ao": "234",
				"cid": 6,
				"dirty": 'true',
				"deleted": 'false',
			},
		]
		python_dict = {
			"username": "temp",
			"records": json.dumps(json_data, ensure_ascii=False),
		}
		response = self.client.post(reverse('times:sync')
			,python_dict)
			#content_type="application/json")
		self.assertEqual(response.content, "ok")
		records = Time.objects.all()
		self.assertEqual(len(records), 1)

	def test_visit_with_user(self):

		python_dict = {
			"username": "abc",
			"friend": "temp",
		}
		response = self.client.post(reverse('times:visit')
			,python_dict)
		self.assertEqual(response.content, "ok")
