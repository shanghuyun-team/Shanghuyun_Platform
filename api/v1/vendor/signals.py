from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission, Group
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from wagtail.models import Page, GroupPagePermission

@receiver(post_migrate)
def create_vendors_group(sender, **kwargs):
    # 只在 wagtailcore migrate 之後執行，確保 Page & Permission 都已建立
    if sender.label != 'wagtailcore':
        return

    # 1. 建立或取得群組
    vendors, _ = Group.objects.get_or_create(name='Vendors')

    # 2. 加入「可存取管理介面」
    access_admin = Permission.objects.get(
        content_type__app_label='wagtailadmin',
        codename='access_admin'
    )
    vendors.permissions.add(access_admin)

    # 3. Profile model 的 change/view 權限
    ct_profile = ContentType.objects.get(app_label='api_v1_account', model='profile')
    for codename in ['change_profile', 'view_profile']:
        perm = Permission.objects.get(content_type=ct_profile, codename=codename)
        vendors.permissions.add(perm)

    # 4. 頁面層級的 CUDR 權限：透過 GroupPagePermission
    root_page = Page.get_first_root_node()
    # 權限對應字串請留意 Wagtail 用的是 model codename
    page_codenames = [
        'add_page', 'change_page', 'delete_page',
        'publish_page','lock_page','view_page'
    ]
    for codename in page_codenames:
        perm = Permission.objects.get(
            content_type__app_label='wagtailcore',
            codename=codename
        )
        GroupPagePermission.objects.get_or_create(
            group=vendors,
            page=root_page,
            permission=perm
        )
