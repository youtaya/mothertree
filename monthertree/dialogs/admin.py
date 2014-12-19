from django.contrib import admin
from dialogs.models import Dialog


class DialogAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields':['handle', 'sender', 'link']}),
        ('Room Name', {'fields': ['room_name']}),
        (None, {'fields': ['content']}),
        ('Create Date', {'fields':['create_date']}),
        ('Create Time', {'fields':['create_time']}),
        ('Content Type', {'fields':['content_type']}),
        #(None, {'fields':['photo', 'audio']}),
        ('Deleted', {'fields': ['deleted']}),
        #('Updated', {'fields': ['updated']}),
    ]

admin.site.register(Dialog, DialogAdmin)
