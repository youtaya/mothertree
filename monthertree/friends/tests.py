from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.client import Client
from models import Friend
from django.utils import timezone
import json
import logging

class recommendTests(TestCase):
	def test_recommend(self):
		response = self.client.get(reverse('friends:recommend'))
		json_list = json.loads(response.content)
		for friend in json_list:
			self.assertEqual(friend['username'], 0)

	def test_sync_with_user(self):
		json_data = [
			{
				"h": "temp",
				"u": "james",
				"p": "123456789",
				"cid": 5,
				"dirty": 'true',
				"d": 'false',
			},
			{
				"h": "temp",
				"u": "amrk",
				"p": "0569786321",
				"cid": 6,
				"dirty": 'true',
				"d": 'false',
			},
		]
		python_dict = {
			"username": "temp",
			"friends": json.dumps(json_data, ensure_ascii=False),
		}
		response = self.client.post(reverse('friends:sync')
			,python_dict)
			#content_type="application/json")
		self.assertEqual(response.content, "ok")
		records = Friend.objects.all()
		self.assertEqual(len(records), 1)
