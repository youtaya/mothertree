from django.db import models

class Time(models.Model):
	handle = models.charField(max_length=200)
	title = models.charField(max_length=200)
	content = models.charField(max_length=200)
	create_date = models.DataTimeField('content create date')
	create_time = models.DateTimeField('content create time')
	content_type = models.IntegerField(default=0)
	photo = models.ImageField(upload_to='Photo')
	audio = models.FilePathField(upload_to='Audio')

	def __unicode__(self):
		return self.content
