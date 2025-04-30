from django.db import models

class Product(models.Model):
    name              = models.CharField("名稱", max_length=100)
    short_description = models.TextField("簡短描述", blank=True)
    price             = models.DecimalField("價格", max_digits=10, decimal_places=2, default=0)
    stock             = models.PositiveIntegerField("庫存", default=0)
    image             = models.FileField("圖片", upload_to="products/")
    created           = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
