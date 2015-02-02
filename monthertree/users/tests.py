from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.client import Client
from users.models import UserInfo
from django.contrib.auth.models import User

class usersTests(TestCase):
	def setUp(self):
		user_1 = User.objects.create(username='12345993')
		user_info_1 = UserInfo.objects.create(user=user_1, nickname='test 01')
		user_2 = User.objects.create(username='13636630387')
		user_info_2 = UserInfo.objects.create(user=user_2, nickname='test 02')

	def test_search_people(self):

		json_data = {
			"username": 12345993,
			"search_str": 13636630387,
		}

		response = self.client.post(reverse('users:search_people'), json_data)

		self.assertEqual(response.content, "ok")
