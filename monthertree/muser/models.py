from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User

class UserProfile(models.Model):
	user = models.ForeignKey(User, unique=True)

	luckyday = models.DateField('lucky day', blank=True, null=True)

	def __unicode__(self):
		return u'Profile of user: %s' % self.user.username

def user_post_save(sender, instance, created, **kwargs):
	"""
	create a user profile when a new account is created
	"""
	if created == True:
		UserProfile.objects.create(user=instance)

post_save.connect(user_post_save, sender=User)