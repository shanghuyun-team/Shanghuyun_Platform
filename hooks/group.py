from wagtail_modeladmin.options import ModelAdmin, modeladmin_register
from django.contrib.auth.models import Group
from wagtail import hooks
from django.urls import re_path

@hooks.register('construct_main_menu')
def hide_menu_items(request, menu_items):
    names_to_hide = {'settings', 'reports', 'help'}
    menu_items[:] = [
        item for item in menu_items
        if not (hasattr(item, 'name') and item.name in names_to_hide)
    ]
