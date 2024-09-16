from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group
from .authorization import Authorization



class PermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'content_type', 'codename')
    search_fields = ('name', 'codename')
    list_filter = ('content_type',)

class AuthorizationAdmin(admin.ModelAdmin):
    # list_display = ('menu',)
    search_fields = ('groups', 'menu')
    list_filter = ('groups', 'menu')


admin.site.register(Authorization, AuthorizationAdmin)