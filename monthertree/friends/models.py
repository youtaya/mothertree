from django.db import models

class Friend(models.Model):
	handle = models.CharField(max_length=100)
	username = models.CharField(max_length=200)
	phone_mobile = models.CharField(max_length=200)
	avatar = models.ImageField(upload_to='avatar')
	description = models.CharField(max_length=200)
	deleted = models.BooleanField(default=False)
	updated = models.DateTimeField(auto_now_add=True)


	def __unicode__(self):
		return self.username
