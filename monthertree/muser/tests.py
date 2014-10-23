from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.client import Client
from models import UserProfile
from django.utils import timezone
from django.contrib.auth.models import User
import json
import logging

class userProfileTests(TestCase):

	def test_set_lucky_day(self):
		temp = User.objects.create(username="temp")
		json_data = [
			{
				"username": "temp",
				"date": "2014-05-16",
			},
		]
		python_dict = {
			"luck": json.dumps(json_data, ensure_ascii=False),
		}
		response = self.client.post(reverse('muser:luckyday')
			,python_dict)

		#self.assertEqual(response.content, "200")
		up = UserProfile.objects.get(user=temp)
		self.assertEqual(str(up.luckyday), "2014-05-11");

	def test_get_lucky_day(self):
		temp = User.objects.create(username="temp")
		json_data = [
			{
				"username": "temp",
				"date": "2014-05-16",
			},
		]
		python_dict = {
			"luck": json.dumps(json_data, ensure_ascii=False),
		}
		response = self.client.post(reverse('muser:luckyday')
			,python_dict)

		json_data = [
			{
				"username": "temp",
			},
		]
		python_dict = {
			"luck": json.dumps(json_data, ensure_ascii=False),
		}
		response = self.client.post(reverse('muser:getday'), python_dict)

		self.assertEqual(response.content, "200")
