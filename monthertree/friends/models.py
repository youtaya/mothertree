from django.db import models
from django.contrib.auth.models import User
from users.models import UserInfo

class Friend(models.Model):
	#handle = models.CharField(max_length=200)
	handle = models.ForeignKey(User)
	friend = models.ForeignKey(UserInfo)
	verify_status = models.IntegerField(default=0)
	name_comment = models.CharField(max_length=200)
	description = models.CharField(max_length=200)
	deleted = models.BooleanField(default=False)
	updated = models.DateTimeField(auto_now_add=True)


	def __unicode__(self):
		return self.username
