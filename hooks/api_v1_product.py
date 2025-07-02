from django.contrib import admin
from wagtail_modeladmin.options import ModelAdmin, modeladmin_register
from api.v1.product.models import Product

class ProductAdmin(ModelAdmin):
    model = Product
    menu_label = "商品管理"
    menu_icon = "tag"
    list_display = ("name", "vendor", "price", "stock")
    list_filter = ("vendor",)
    search_fields = ("name", "vendor__company_name")
modeladmin_register(ProductAdmin)