from django.db import models
from django.contrib.auth.models import User
from users.models import UserInfo

class Friend(models.Model):
	#handle = models.CharField(max_length=200)
	handle = models.ForeignKey(User, related_name='creator')
	friend = models.ForeignKey(User, related_name='inviter')
	verify_status = models.IntegerField(default=0)
	name_comment = models.CharField(max_length=200)
	description = models.CharField(max_length=200)
	deleted = models.BooleanField(default=False)
	updated = models.DateTimeField(auto_now_add=True)


	def __unicode__(self):
		return self.username

	def get_friend_info(self):
		data = {}
		data['friend'] = self.friend.username
		user_info = UserInfo.objects.get(user=self.friend)
		data['avatar'] = user_info.avatar_url()
		return data
