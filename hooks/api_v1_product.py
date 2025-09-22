from wagtail_modeladmin.options import ModelAdmin, modeladmin_register 
from wagtail_modeladmin.views import CreateView, EditView
from wagtail.admin.panels import FieldPanel
from api.v1.product.models import Product
from api.v1.vendor.models import Vendor
from wagtail import hooks

class ProductCreateView(CreateView):
    def form_valid(self, form):
        if self.request.user.is_superuser:
            # cleaned_data 只有在 is_valid() 通過後才有
            vendor = form.cleaned_data.get('vendor')
        else:
            # 一般 vendor 自動綁定
            if not form.instance.pk:
                if not getattr(self.request.user, 'vendor_profile', None):
                    vendor = Vendor.objects.create(
                        user=self.request.user,
                        company_name=self.request.user.email
                    )
                    self.request.user.vendor_profile = vendor
                form.instance.vendor = self.request.user.vendor_profile
        return super().form_valid(form)
    
class ProductAdmin(ModelAdmin):
    model = Product
    menu_label    = "商品管理"
    menu_icon     = "tag"
    list_display  = ("name", "vendor", "price", "stock")
    list_filter   = ("vendor",)
    search_fields = ("name", "vendor__company_name",)

    create_view_class = ProductCreateView

    panels = [
        FieldPanel('vendor', permission='superuser'),
        FieldPanel('name'),
        FieldPanel('description'),
        FieldPanel('price'),
        FieldPanel('stock'),
        FieldPanel('image'),
    ]

    def is_shown(self, request):
        return request.user.is_authenticated and (
            request.user.is_superuser or getattr(request.user, 'is_vendor', False)
        )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs if request.user.is_superuser else qs.filter(vendor__user=request.user)

modeladmin_register(ProductAdmin)


@hooks.register("construct_image_chooser_queryset")
def _limit_image_chooser_to_own_uploads(images, request):
    """
    非超級管理員/非員工：圖片挑選器只顯示自己上傳的圖片
    超管/員工：不受限
    """
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return images
    if user.is_superuser or user.is_staff:
        return images
    return images.filter(uploaded_by_user=user)


@hooks.register("construct_image_index_queryset")
def _limit_image_index_to_own_uploads(images, request):
    """
    非超級管理員/非員工：圖片列表只顯示自己上傳的圖片
    超管/員工：不受限
    """
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return images
    if user.is_superuser or user.is_staff:
        return images
    return images.filter(uploaded_by_user=user)