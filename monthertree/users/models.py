from django.db import models
from django.contrib.auth.models import User
from django.forms import ModelForm

class UserInfo(models.Model):
    user = models.OneToOneField(User)
    nickname = models.CharField(max_length=24, blank=True)
    avatar = models.ImageField(upload_to='avatar')
    reserved = models.CharField(max_length=140)

class UserInfoForm(ModelForm):
    class Meta:
        model = UserInfo
        fields = ['nickname', 'avatar']
