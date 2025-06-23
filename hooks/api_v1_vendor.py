# your_app/wagtail_hooks.py

from wagtail import hooks
from wagtail.models import Page
from django.core.exceptions import PermissionDenied

# 1. 建立頁面時自動設定 owner
@hooks.register('before_create_page')
def set_owner(request, page):
    page.owner = request.user

# 2. 編輯前檢查：非 owner 一律拒絕
@hooks.register('before_edit_page')
def check_before_edit(request, page):
    if page.owner_id != request.user.id:
        raise PermissionDenied

# 3. 刪除前檢查
@hooks.register('before_delete_page')
def check_before_delete(request, page):
    if page.owner_id != request.user.id:
        raise PermissionDenied

# 4. 發佈／取消發佈前檢查
@hooks.register('before_publish_page')
@hooks.register('before_unpublish_page')
def check_before_publish(request, page):
    if page.owner_id != request.user.id:
        raise PermissionDenied

# 5. 在 Explorer 中只顯示自己的頁面
@hooks.register('construct_explorer_page_queryset')
def show_only_own_pages(request, pages, parent_page):
    if request.user.groups.filter(name='Vendors').exists():
        return pages.filter(owner=request.user)
    return pages
