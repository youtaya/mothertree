from django import forms

class UploadFileForm(forms.Form):
	body = forms.CharField(max_length=50)
	image = forms.FileField()