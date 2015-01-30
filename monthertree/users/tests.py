from django.test import TestCase

class friendsTests(TestCase):
	def test_search_friend(self):
		self.prepare_data()

		json_data = {
			"username": 12345993,
			"search_str": 13636630387,
		}

		response = self.client.post(reverse('friends:search_friend'), json_data)

		self.assertEqual(response.content, "ok")
