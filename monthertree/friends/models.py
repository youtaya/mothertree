from django.db import models
from django.contrib.auth.models import User

class Friend(models.Model):
	#handle = models.CharField(max_length=200)
	handle = models.ForeignKey(User)
	username = models.CharField(max_length=200)
	mobile_phone = models.CharField(max_length=200)
	avatar = models.ImageField(upload_to='avatar')
	verify_status = models.IntegerField(default=0)
	name_comment = models.CharField(max_length=200)
	description = models.CharField(max_length=200)
	deleted = models.BooleanField(default=False)
	updated = models.DateTimeField(auto_now_add=True)


	def __unicode__(self):
		return self.username
