# project/v1/account/wagtail_hooks.py
from wagtail_modeladmin.options import ModelAdmin, modeladmin_register
from .models import User

class UserModelAdmin(ModelAdmin):
    model = User
    menu_label = "使用者"
    menu_icon = "user"
    list_display = ("username", "real_name", "is_vendor", "is_active")
    search_fields = ("username", "real_name", "email")

modeladmin_register(UserModelAdmin)
