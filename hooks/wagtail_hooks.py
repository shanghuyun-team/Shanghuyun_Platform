from .api_v1_account import *
from .group import *

from wagtail.admin.menu import MenuItem
from wagtail import hooks
from django.utils.translation import gettext_lazy as _

@hooks.register('construct_main_menu')
def add_homepage_link(request, menu_items):
    menu_items.append(
        MenuItem(
            label=_("回到首頁"),
            url="/",
            icon_name="home",
            classname="custom-home-link",
            order=10000,
            attrs={"target": "_blank"}
        )
    )