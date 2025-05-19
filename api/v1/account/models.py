from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager
)
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField

class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('必須提供 username')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        return self.create_user(username, password=password, **extra_fields)

    def create_vendor(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_vendor', True)
        return self.create_user(username, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username    = models.CharField('用戶名', max_length=150, unique=True)
    is_active   = models.BooleanField('是否啟用', default=True)
    is_staff    = models.BooleanField('是否員工', default=False)
    is_vendor   = models.BooleanField('是否商家', default=False)
    date_joined = models.DateTimeField('加入時間', auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username


class Profile(models.Model):
    user        = models.OneToOneField(
                      settings.AUTH_USER_MODEL,
                      on_delete=models.CASCADE,
                      related_name='profile'
                  )
    real_name   = models.CharField('真實姓名', max_length=20, blank=True, null=True)
    nickname    = models.CharField('暱稱', max_length=20, blank=True, null=True)
    email       = models.EmailField('電子郵件', unique=True, blank=True, null=True)
    portrait    = models.ImageField(
                      '頭像',
                      upload_to='user/portrait/',
                      blank=True, null=True
                  )
    address     = models.CharField('通訊地址', max_length=255, blank=True, null=True)
    phone       = PhoneNumberField('手機號碼', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}_Profile"
