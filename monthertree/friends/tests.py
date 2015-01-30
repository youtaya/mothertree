from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.client import Client
from models import Friend
from django.contrib.auth.models import User
from django.utils import timezone
import json
import logging

class recommendTests(TestCase):
	def SetUp(self):
		user_1 = User.objects.create(username='12345993')
		user_info_1 = UserInfo.objects.create(user=user_1, nickname='test 01')
		user_2 = User.objects.create(username='13636630387')
		user_info_2 = UserInfo.objects.create(user=user_2, nickname='test 02')

	def test_recommend(self):
		response = self.client.get(reverse('friends:recommend'))
		json_list = json.loads(response.content)
		for friend in json_list:
			self.assertEqual(friend['username'], 0)

	def test_add_friend(self):
		json_data = {
			'mobile': '12345993',
			"friend_mobile": '13636630387',
		}

		response = self.client.post(reverse('friend:add_friend'), json_data)

		self.assertEqual(response.content, "ok")

	def test_get_friend_less(self):
		self.prepare_data()

		json_data = {
			"mobile": '12345993',
			"local_friend_version": 1,
		}

		response = self.client.post(reverse('friend:get_friend'), json_data)

		self.assertEqual(response.content, "ok")

	def test_get_friend_equality(self):
		self.prepare_data()

		json_data = {
			"mobile": '12345993',
			"local_friend_version": 2,
		}

		response = self.client.post(reverse('friend:get_friend'), json_data)

		self.assertEqual(response.content, "ok")

	def test_accept_friend(self):
		json_data = {
			"mobile": 12345993,
			"nok": 1,
			"friend_mobile": 13636630387,
		}

		response = self.client.post(reverse('friend:accept_friend'), json_data)

		self.assertEqual(response.content, "ok")

	def test_update_friend(self):
		self.prepare_data()

		json_data = {
			"mobile": 12345993,
			"friend_mobile": 13636630387,
			"comment": 'penut',
			"group": 'cat_pic',
			"description": 'cross finger',
		}

		response = self.client.post(reverse('friend:update_friend'), json_data)

		self.assertEqual(response.content, "ok")

	def test_search_friend(self):
		self.prepare_data()

		json_data = {
			"mobile": 12345993,
			"search_str": 13636630387,
		}

		response = self.client.post(reverse('friend:search_friend'), json_data)

		self.assertEqual(response.content, "ok")

	def test_sync_friend_with_user(self):
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

	def prepare_data(self):
		test1 = User.objects.get(username='12345993')
		dog = UserInfo.objects.get(user=test1)
		cat = Friend.objects.create(user=test1,phone='13636630387', nickname='cat',version_id=1)
		cow = Friend.objects.create(user=test1, phone='13636630388', nickname='cow',version_id=2)
