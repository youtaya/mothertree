from django.db import models

class Dialog(models.Model):
    id = models.AutoField(primary_key=True)
    handle = models.CharField(max_length=100)
    room_name = models.CharField(max_length=100)
    sender = models.CharField(max_length=100)
    link = models.CharField(max_length=100)
    content = models.CharField(max_length=300)
    create_date = models.CharField(max_length=200)
    create_time = models.CharField(max_length=200)
    content_type = models.IntegerField(default=0)
    photo = models.ImageField(upload_to='Photo')
    audio = models.FileField(upload_to='Audio')
    deleted = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now_add=True)


    def __unicode__(self):
        return self.content

    @classmethod
    def get_record_create_time(cls, time):
        if create_time not in (None, ''):
            query = cls.objects.get(create_time=time)
            return query
        return None
