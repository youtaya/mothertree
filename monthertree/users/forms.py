from django import forms

class UploadFileForm(forms.Form):
	image = forms.FileField()

class UserInfoForm(forms.Form):
    nickname = forms.CharField(max_length=24)
    avatar = forms.FileField()
