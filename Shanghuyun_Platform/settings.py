from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------------------------------------------------------
# 基本設定
# ------------------------------------------------------------------------------
# 安全金鑰 (production 使用者請透過環境變數或 vault 管理)
SECRET_KEY = 'django-insecure-8^rgyjljdddhi7hhsl1#q%u_)3_0m6k4y+fctov2cqvgf1_h%&'
# 調試模式 (production 請設為 False)
DEBUG = True
# 主機允許清單
ALLOWED_HOSTS = ['*']

# ------------------------------------------------------------------------------
# 應用程式定義
# ------------------------------------------------------------------------------
INSTALLED_APPS = [
    # 管理介面
    'jazzmin',
    # Django 內建套件
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 自訂 App
    'apps.home.apps.HomeConfig',
    'apps.profile_info.apps.ProfileInfoConfig',
    'apps.sale.apps.SaleConfig',
    'apps.vendor_dashboard.apps.VendorDashboardConfig',
    # API
    'api.v1.apps.V1Config',
    # 第三方套件
    "allauth_ui", 'allauth', 'allauth.account', 'allauth.socialaccount', 'django.contrib.sites',
    "widget_tweaks", "slippers", 'rest_framework', 'django_drf_filepond', 'storages',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # Allauth 中間件
]

ROOT_URLCONF = 'Shanghuyun_Platform.urls'
SITE_ID = 1  # django.contrib.sites 配置

# ------------------------------------------------------------------------------
# 模板設定
# ------------------------------------------------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # 全域模板目錄
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.home.context_processors.common_static',  # 自訂靜態資源路徑
            ],
        },
    },
]

WSGI_APPLICATION = 'Shanghuyun_Platform.wsgi.application'

# ------------------------------------------------------------------------------
# 資料庫設定 (SQLite for development)
# ------------------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ------------------------------------------------------------------------------
# 密碼驗證 (可按需調整)
# ------------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ------------------------------------------------------------------------------
# 語言與時區
# ------------------------------------------------------------------------------
LANGUAGE_CODE = 'zh-hant'
TIME_ZONE = 'Asia/Taipei'
USE_I18N = True
USE_TZ = True

# ------------------------------------------------------------------------------
# 靜態檔案 (CSS, JS, Images)
# ------------------------------------------------------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# ------------------------------------------------------------------------------
# 預設主鍵欄位類型
# ------------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ------------------------------------------------------------------------------
# Django DRF FilePond / Cloudflare R2 儲存設定
# ------------------------------------------------------------------------------
# 暫存目錄由 django-drf-filepond 控制 (filepond_uploads)
# 永久儲存使用自訂 R2 存儲後端
DEFAULT_FILE_STORAGE = 'apps.home.storages.R2Boto3Storage'
DJANGO_DRF_FILEPOND_STORAGES_BACKEND = DEFAULT_FILE_STORAGE

# R2 S3 API 憑證與參數
AWS_ACCESS_KEY_ID        = '66abb83de3dec1377ecd76df54bedde0'
AWS_SECRET_ACCESS_KEY    = 'a09f43f7d8d06649f0cd6f6bd8c3fcb3d7c003ca70478fe9e76a13c5a60b1e71'
AWS_STORAGE_BUCKET_NAME  = 'shanghuyun-platform'
AWS_S3_ENDPOINT_URL      = 'https://4e9bbe760333a36bd94fad22caccc552.r2.cloudflarestorage.com'
AWS_S3_REGION_NAME       = None
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_DEFAULT_ACL          = None

# Media 由 R2.dev 子域公開 (使用 Storage.custom_domain)
MEDIA_URL = f"https://pub-5049d4dc36de483ab78891fd244767be.r2.dev/"
# MEDIA_ROOT = BASE_DIR / 'media'  # 可選保留，但不影響 R2 存取

# ------------------------------------------------------------------------------
# Jazzmin 介面自訂設定
# ------------------------------------------------------------------------------

#############################################################
JAZZMIN_SETTINGS = {
    # title of the window (Will default to current_admin_site.site_title if absent or None)
    "site_title": "Library Admin",

    # Title on the login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_header": "管理介面",

    # Title on the brand (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_brand": "管理介面",

    # Logo to use for your site, must be present in static files, used for brand on top left
    "site_logo": 'assets/images/favicon.png',

    # Logo to use for your site, must be present in static files, used for login form logo (defaults to site_logo)
    "login_logo": None,

    # Logo to use for login form in dark themes (defaults to login_logo)
    "login_logo_dark": None,

    # CSS classes that are applied to the logo above
    "site_logo_classes": "img-circle",

    # Relative path to a favicon for your site, will default to site_logo if absent (ideally 32x32 px)
    "site_icon": None,

    # Welcome text on the login screen
    "welcome_sign": "歡迎來到管理介面，請先登入",

    # Copyright on the footer
    "copyright": "尚虎雲產銷平台",

    # List of model admins to search from the search bar, search bar omitted if excluded
    # If you want to use a single search field you dont need to use a list, you can use a simple string 
    "search_model": ["auth.User", "auth.Group"],

    # Field name on user model that contains avatar ImageField/URLField/Charfield or a callable that receives the user
    "user_avatar": None,

    ############
    # Top Menu #
    ############

    # Links to put along the top menu
    "topmenu_links": [

        # Url that gets reversed (Permissions can be added)
        {"name": "Home",  "url": "admin:index", "permissions": ["auth.view_user"]},

        # external url that opens in a new window (Permissions can be added)
        {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},

        # model admin to link to (Permissions checked against model)
        {"model": "auth.User"},

        # App with dropdown menu to all its models pages (Permissions checked against models)
        {"app": "books"},
    ],

    #############
    # User Menu #
    #############

    # Additional links to include in the user menu on the top right ("app" url type is not allowed)
    "usermenu_links": [
        {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},
        {"model": "auth.user"}
    ],

    #############
    # Side Menu #
    #############

    # Whether to display the side menu
    "show_sidebar": True,

    # Whether to aut expand the menu
    "navigation_expanded": True,

    # Hide these apps when generating side menu e.g (auth)
    "hide_apps": [],

    # Hide these models when generating side menu (e.g auth.user)
    "hide_models": [],

    # List of apps (and/or models) to base side menu ordering off of (does not need to contain all apps/models)
    "order_with_respect_to": ["auth", "books", "books.author", "books.book"],

    # Custom links to append to app groups, keyed on app name
    "custom_links": {
        "books": [{
            "name": "Make Messages", 
            "url": "make_messages", 
            "icon": "fas fa-comments",
            "permissions": ["books.view_book"]
        }]
    },

    # Custom icons for side menu apps/models See https://fontawesome.com/icons?d=gallery&m=free&v=5.0.0,5.0.1,5.0.10,5.0.11,5.0.12,5.0.13,5.0.2,5.0.3,5.0.4,5.0.5,5.0.6,5.0.7,5.0.8,5.0.9,5.1.0,5.1.1,5.2.0,5.3.0,5.3.1,5.4.0,5.4.1,5.4.2,5.13.0,5.12.0,5.11.2,5.11.1,5.10.0,5.9.0,5.8.2,5.8.1,5.7.2,5.7.1,5.7.0,5.6.3,5.5.0,5.4.2
    # for the full list of 5.13.0 free icon classes
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
    },
    # Icons that are used when one is not manually specified
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",

    #################
    # Related Modal #
    #################
    # Use modals instead of popups
    "related_modal_active": False,

    #############
    # UI Tweaks #
    #############
    # Relative paths to custom CSS/JS scripts (must be present in static files)
    "custom_css": None,
    "custom_js": None,
    # Whether to link font from fonts.googleapis.com (use custom_css to supply font otherwise)
    "use_google_fonts_cdn": True,
    # Whether to show the UI customizer on the sidebar
    "show_ui_builder": False,

    ###############
    # Change view #
    ###############
    # Render out the change view as a single form, or in tabs, current options are
    # - single
    # - horizontal_tabs (default)
    # - vertical_tabs
    # - collapsible
    # - carousel
    "changeform_format": "horizontal_tabs",
    # override change forms on a per modeladmin basis
    "changeform_format_overrides": {"auth.user": "collapsible", "auth.group": "vertical_tabs"},
    # Add a language dropdown into the admin
    "language_chooser": False,
}
#############################################################
