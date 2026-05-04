from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-eykl)^f^^t1jfwvvx0yj1)1_b)y%$vd!u&dof3%6nnn)!(c=2-"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

# 開發環境使用簡單的靜態檔案存儲（不需要 collectstatic）
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}


try:
    from .local import *
except ImportError:
    pass

