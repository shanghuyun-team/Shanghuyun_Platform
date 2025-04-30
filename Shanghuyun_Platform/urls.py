"""
URL configuration for Shanghuyun_Platform project.

This module defines the URL routes for the entire Django project, including:
  - Admin site
  - Frontend sale and dashboard apps
  - REST API (v1)
  - Authentication (logout)

When DEBUG is True, also serves media files via Django's static helper.
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib.auth.views import LogoutView as auth_views

urlpatterns = [
    # Django Admin site
    path('admin/', admin.site.urls),

    # 銷售模組：前端販售頁面路由，apps.sale.urls 負責具體 view mapping
    path('sales/', include('apps.sale.urls')),

    # 賣家後台 Dashboard：商家管理介面，apps.vendor_dashboard.urls 定義子路由
    path('dashboard/', include('apps.vendor_dashboard.urls')),

    # REST API v1：統一的 API endpoints，包含 Product 及其他資源
    path('api/v1/', include('api.v1.urls')),

    # 登出路由：使用 Django 內建 LogoutView
    path('logout/', auth_views.as_view(), name='logout'),
]

# 僅在開發模式下，使用 Django 內建 static helper 來提供 MEDIA_URL  & MEDIA_ROOT
# 上傳的檔案會透過 settings.MEDIA_URL 對應到 settings.MEDIA_ROOT
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
