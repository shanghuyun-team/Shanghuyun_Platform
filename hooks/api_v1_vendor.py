from wagtail_modeladmin.options import ModelAdmin, modeladmin_register
from api.v1.vendor.models import Vendor

class VendorAdmin(ModelAdmin):
    model = Vendor
    menu_label = "商家管理"         # 左側選單顯示文字
    menu_icon = "user"             # 🡐 Wagtail icon name
    list_display = ("company_name", "user", "phone")
    search_fields = ("company_name", "user__email")
modeladmin_register(VendorAdmin)
