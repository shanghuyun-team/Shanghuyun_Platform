# hooks/wagtail_hooks.py
from .api_v1_account import *
from wagtail import hooks
from django.urls import re_path
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

@hooks.register('construct_main_menu')
def hide_menu_items(request, menu_items):
    # 永遠隱藏的
    names_to_hide = {'settings', 'reports', 'help'}
    # 非 vendor 時也要隱藏的
    if not getattr(request.user, 'is_vendor', False):
        names_to_hide |= {'explorer', 'images', 'documents'}
    # 過濾
    menu_items[:] = [
        item for item in menu_items
        if not (hasattr(item, 'name') and item.name in names_to_hide)
    ]
