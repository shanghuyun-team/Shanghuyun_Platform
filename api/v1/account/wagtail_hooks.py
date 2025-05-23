from wagtail import hooks
from django.urls import re_path
from django.http import HttpResponseNotFound

from wagtail_modeladmin.options import ModelAdmin, modeladmin_register
from allauth.account.models import EmailAddress
from .models import User#, Profile
from django.template.response import TemplateResponse


@hooks.register('register_admin_urls')
def hide_users_admin_urls():
    def users_not_found(request, *args, **kwargs):
        return TemplateResponse(request, 'wagtailadmin/404.html', status=404)

    return [
        # hide all /admin/users/
        re_path(
            r"^users/.*$",
            users_not_found,
            name="hide_wagtail_users"
        ),
    ]


class UserAdmin(ModelAdmin):
    model = User
    menu_label = '用戶管理'
    menu_icon = 'user'
    list_display = ('email', 'email_verified', 'is_active', 'is_staff', 'is_vendor')
    search_fields = ('email',)

    def email_verified(self, obj):
        return EmailAddress.objects.filter(
            user=obj,
            email=obj.email,
            verified=True
        ).exists()
    email_verified.boolean = True
    email_verified.short_description = '信箱已驗證'

modeladmin_register(UserAdmin)

"""
class ProfileAdmin(ModelAdmin):
    model = Profile
    menu_label = '個人檔案'
    menu_icon = 'form'
    list_display = ('user', 'email', 'real_name', 'nickname')
    search_fields = ('user__username', 'email', 'real_name')

modeladmin_register(ProfileAdmin)
"""