from .api_v1_account import *
from .api_v1_vendor import *
from .api_v1_product import *
from .group import *

from wagtail.admin.menu import MenuItem
from wagtail import hooks
from django.urls import reverse

# 載入你的 Setting model
from apps.users.models.privacy_policy import SitePolicySetting

@hooks.register('construct_main_menu')
def add_homepage_link(request, menu_items):
    menu_items.append(
        MenuItem(
            label="回到首頁",
            url="/",
            icon_name="home",
            classname="custom-home-link",
            order=10000,
            attrs={"target": "_blank"}
        )
    )

@hooks.register('register_admin_menu_item')
def register_privacy_policy_menu_item():
    # 取出正確的 app_label 跟 model_name
    app_label  = SitePolicySetting._meta.app_label      # -> "users"
    model_name = SitePolicySetting._meta.model_name     # -> "sitepolicysetting"
    url = reverse('wagtailsettings:edit', args=[app_label, model_name])

    return MenuItem(
        '隱私權政策',           
        url,                   
        icon_name='doc-full-inverse',  
        order=300              
    )
