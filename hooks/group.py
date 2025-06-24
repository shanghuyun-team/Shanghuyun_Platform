from wagtail_modeladmin.options import ModelAdmin, modeladmin_register
from django.contrib.auth.models import Group
from wagtail import hooks
from django.urls import re_path

class GroupModelAdmin(ModelAdmin):
    model = Group
    menu_label = "群組管理"     # 側邊選單顯示文字
    menu_icon = "group"       # Lucide icon name
    list_display = ("name",)
    # 需要讓管理者看到 user_set，就在 form 裡加上 groups 反向欄位
    form_fields_exclude = []
    form_fields = ['name', 'permissions', 'user_set']
modeladmin_register(GroupModelAdmin)

@hooks.register('construct_main_menu')
def hide_menu_items(request, menu_items):
    names_to_hide = {'settings', 'reports', 'help'}
    menu_items[:] = [
        item for item in menu_items
        if not (hasattr(item, 'name') and item.name in names_to_hide)
    ]
