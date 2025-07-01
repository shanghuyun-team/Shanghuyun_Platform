from django.db import models
from django.conf import settings

class Vendor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vendor_profile'
    )
    company_name = models.CharField('公司名稱', max_length=100)
    tax_id       = models.CharField('統一編號', max_length=20, blank=True, null=True)
    address      = models.CharField('公司地址', max_length=255, blank=True, null=True)
    phone        = models.CharField('聯絡電話', max_length=20, blank=True, null=True)
    created_at   = models.DateTimeField('建立時間', auto_now_add=True)
    updated_at   = models.DateTimeField('更新時間', auto_now=True)

    def __str__(self):
        return f"{self.company_name} ({self.user.email})"