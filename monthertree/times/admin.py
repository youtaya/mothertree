from django.contrib import admin
from times.models import Time


class TimeAdmin(admin.ModelAdmin):
	fieldsets = [
		(None, {'fields':['handle', 'title']}),
		(None, {'fields': ['content']}),
		('Create Date', {'fields':['create_date']}),
		('Create Time', {'fields':['create_time']}),
		('Content Type', {'fields':['content_type']}),
		# (None, {'fields':['photo', 'audio']}),
	]

admin.site.register(Time, TimeAdmin)
