from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Follow


class UserAdmin(UserAdmin):
    list_filter = ('id', 'email', 'username')


class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
