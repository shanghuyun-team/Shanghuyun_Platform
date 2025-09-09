from wagtail.admin.menu import MenuItem
from wagtail import hooks
from django.urls import reverse
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

# 載入網站基本設定模型
from apps.home.models import SiteBasicSetting
from apps.users.models.privacy_policy import SitePolicySetting
from apps.users.models.terms_of_service import SiteTermsSetting


@hooks.register('register_admin_menu_item')
def register_site_basic_setting_menu_item():
    """
    註冊網站基本設定選單項目
    只有超級管理員可以看到此選單
    """
    # 取出正確的 app_label 跟 model_name
    app_label = SiteBasicSetting._meta.app_label      # -> "home"
    model_name = SiteBasicSetting._meta.model_name    # -> "sitebasicsetting"
    url = reverse('wagtailsettings:edit', args=[app_label, model_name])

    return MenuItem(
        '網站基本設定',           
        url,                   
        icon_name='cogs',  
        order=100,              # 設定較高的優先級
        classname='icon icon-cogs',
    attrs={'title': '僅限超級管理員'}
    )


@hooks.register('register_admin_menu_item')
def register_privacy_policy_menu_item():
    """
    註冊隱私權政策設定選單項目
    只有超級管理員可以看到此選單
    """
    app_label = SitePolicySetting._meta.app_label      # -> "users"
    model_name = SitePolicySetting._meta.model_name    # -> "sitepolicysetting"
    url = reverse('wagtailsettings:edit', args=[app_label, model_name])

    return MenuItem(
        '隱私權政策設定',           
        url,                   
        icon_name='privacy',  
        order=101,              
        classname='icon icon-privacy',
        attrs={'title': '僅限超級管理員'}
    )


@hooks.register('register_admin_menu_item')
def register_terms_of_service_menu_item():
    """
    註冊服務條款設定選單項目
    只有超級管理員可以看到此選單
    """
    app_label = SiteTermsSetting._meta.app_label      # -> "users"
    model_name = SiteTermsSetting._meta.model_name    # -> "sitetermssetting"
    url = reverse('wagtailsettings:edit', args=[app_label, model_name])

    return MenuItem(
        '服務條款',           
        url,                   
        icon_name='doc-full',  
        order=102,              
        classname='icon icon-doc-full',
        attrs={'title': '僅限超級管理員'}
    )


@hooks.register('construct_main_menu')
def hide_site_settings_for_non_superusers(request, menu_items):
    """
    確保非超級管理員無法看到網站設定相關選單
    """
    if not request.user.is_superuser:
        # 移除任何可能的網站設定選單項目
        menu_items_to_remove = []
        for item in menu_items:
            if hasattr(item, 'label') and ('網站基本設定' in item.label or '隱私權政策' in item.label or '服務條款' in item.label):
                menu_items_to_remove.append(item)
        
        for item in menu_items_to_remove:
            menu_items.remove(item)


@hooks.register('before_edit_snippet')
def check_site_settings_permissions(request, instance):
    """
    檢查編輯網站設定的權限
    只有超級管理員可以編輯
    """
    if isinstance(instance, (SiteBasicSetting, SitePolicySetting, SiteTermsSetting)):
        if not request.user.is_superuser:
            from django.core.exceptions import PermissionDenied
            model_name = instance._meta.verbose_name
            raise PermissionDenied(f"只有超級管理員可以編輯{model_name}")


@hooks.register('before_create_snippet')
def check_site_settings_create_permissions(request, model):
    """
    檢查創建網站設定的權限
    只有超級管理員可以創建
    """
    if model in [SiteBasicSetting, SitePolicySetting, SiteTermsSetting]:
        if not request.user.is_superuser:
            from django.core.exceptions import PermissionDenied
            model_name = model._meta.verbose_name
            raise PermissionDenied(f"只有超級管理員可以創建{model_name}")


@hooks.register('register_permissions')
def register_site_settings_permissions():
    """
    註冊網站設定的自訂權限
    """
    permissions = []
    
    # 註冊網站基本設定權限
    basic_content_type = ContentType.objects.get_for_model(SiteBasicSetting)
    permissions.extend(Permission.objects.filter(
        content_type=basic_content_type,
        codename__in=['can_edit_site_settings']
    ))
    
    # 註冊隱私權政策權限
    policy_content_type = ContentType.objects.get_for_model(SitePolicySetting)
    permissions.extend(Permission.objects.filter(
        content_type=policy_content_type,
        codename__in=['can_edit_privacy_policy']
    ))
    
    # 註冊服務條款權限
    terms_content_type = ContentType.objects.get_for_model(SiteTermsSetting)
    permissions.extend(Permission.objects.filter(
        content_type=terms_content_type,
        codename__in=['can_edit_terms_of_service']
    ))
    
    return permissions
