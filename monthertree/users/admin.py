from django.contrib import admin
from users.models import UserInfo


class UserInfoAdmin(admin.ModelAdmin):
	fieldsets = [
		('user', {'fields':['user']}),
		('nickname', {'fields': ['nickname']}),
		('avatar', {'fields': ['avatar']}),
	]

admin.site.register(UserInfo, UserInfoAdmin)
