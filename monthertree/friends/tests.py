from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.client import Client
from models import Friend
from django.utils import timezone
from bson.json_util import default, object_hook
import json
import logging

class recommendTests(TestCase):
	def test_recommend(self):
		response = self.client.get(reverse('friends:recommend'))
		json_list = json.loads(response.content, object_hook=object_hook)
		for friend in json_list:
			self.assertEqual(friend['username'], 0)