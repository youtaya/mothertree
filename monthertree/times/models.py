from django.db import models

class Time(models.Model):
	handle = models.CharField(max_length=100)
	title = models.CharField(max_length=200)
	content = models.CharField(max_length=300)
	create_date = models.DateTimeField('content date')
	create_time = models.DateTimeField('content time')
	content_type = models.IntegerField(default=0)
	photo = models.ImageField(upload_to='Photo')
	audio = models.FileField(upload_to='Audio')
	status = models.CharField(max_length=50)
	deleted = models.CharField(max_length=50)
	updated = models.CharField(max_length=50)


	def __unicode__(self):
		return self.content
