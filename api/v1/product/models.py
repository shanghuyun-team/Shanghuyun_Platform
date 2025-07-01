from django.db import models
from api.v1.vendor.models import Vendor


class Product(models.Model):
    vendor      = models.ForeignKey(
                      Vendor,
                      on_delete=models.CASCADE,
                      related_name='products'
                  )
    name        = models.CharField('商品名稱', max_length=100)
    description = models.TextField('商品描述', blank=True)
    price       = models.DecimalField('售價', max_digits=10, decimal_places=2)
    stock       = models.PositiveIntegerField('庫存量', default=0)
    image       = models.ImageField('商品圖片', upload_to='products/', blank=True, null=True)
    created_at  = models.DateTimeField('建立時間', auto_now_add=True)
    updated_at  = models.DateTimeField('更新時間', auto_now=True)

    def __str__(self):
        return self.name