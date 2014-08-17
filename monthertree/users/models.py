from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User

class UserProfile(models.Model):
	user = models.ForeignKey(User, unique=True, verbose_name='extra info')

	luckyday = models.DateField('lucky day', blank=True, null=True)

def user_post_save(sender, instance, created, **kwargs):
	"""
	create a user profile when a new account is created
	"""
	if created == True:
		p = UserProfile()
		p.user = instance
		p.save()

post_save.connect(user_post_save, sender=User)