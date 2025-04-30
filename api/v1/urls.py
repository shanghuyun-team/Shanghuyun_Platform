from django.urls import re_path, include, path
from rest_framework.routers import DefaultRouter
from api.v1.views import ProductViewSet

# 建立 DRF 的 router，會自動生成 CRUD 路由
router = DefaultRouter()
# 將 ProductViewSet 註冊到 router，路由前綴為 "products"
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    # FilePond 處理上傳、取消、載入等端點，統一掛載到 /fp/ 路徑下
    re_path(r'^fp/', include('django_drf_filepond.urls')),
    # 將 router 生成的所有 API 路由掛載到根路徑
    path('', include(router.urls)),
]
