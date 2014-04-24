from django.db import models

class Time(models.Model):
	handle = models.CharField(max_length=100)
	title = models.CharField(max_length=200)
	content = models.CharField(max_length=300)
	create_date = models.DateField('content date')
	create_time = models.DateTimeField('content time')
	content_type = models.IntegerField(default=0)
	photo = models.ImageField(upload_to='Photo')
	audio = models.FileField(upload_to='Audio')
	status = models.CharField(max_length=50)
	deleted = models.BooleanField()
	updated = models.DateTimeField(auto_now=True, auto_now_add=True)


	def __unicode__(self):
		return self.content
