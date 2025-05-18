from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField

class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, password=password, **extra_fields)

    def create_vendor(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_vendor", True)
        return self.create_user(username, password=password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    username    = models.CharField(verbose_name="用戶名", max_length=20, unique=True)
    real_name   = models.CharField(verbose_name="真實姓名", max_length=20, blank=True, null=True)
    nickname    = models.CharField(verbose_name="暱稱", max_length=20, blank=True, null=True)
    email       = models.EmailField(verbose_name="電子郵件", unique=True, blank=True, null=True)
    portrait    = models.ImageField(verbose_name="頭像", upload_to="user/portrait", blank=True, null=True)
    address     = models.CharField(verbose_name="住址", max_length=255, blank=True, null=True)
    phone       = PhoneNumberField(verbose_name="手機號碼", blank=True, null=True)
    is_active   = models.BooleanField(verbose_name="是否啟用", default=True)
    is_vendor   = models.BooleanField(verbose_name="是否商家", default=False)
    date_joined = models.DateTimeField(verbose_name="加入時間", auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "使用者"
        verbose_name_plural = "使用者"
        indexes = [
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return self.username