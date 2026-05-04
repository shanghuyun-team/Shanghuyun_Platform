from django.db import models
from api.v1.product.models import Product
from api.v1.account.models import User
import uuid


class Order(models.Model):
    STATUS_PENDING = "pending"
    STATUS_PAID = "paid"
    STATUS_FAILED = "failed"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default=STATUS_PENDING)  # pending / paid / failed
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)  # 付款時間
    merchant_trade_no = models.CharField(max_length=20, blank=True, unique=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 暫存原始狀態，避免 save() 中再查一次 DB
        self._original_status = self.status

    def get_total_items_count(self):
        """獲取訂單中商品總數量"""
        return sum(item.quantity for item in self.items.all())

    def recalculate_total(self):
        """重新計算訂單總金額"""
        total = sum(item.get_total() for item in self.items.all())
        self.total_amount = total
        return total

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        # 新訂單：先存一次產生 ID，再生成 merchant_trade_no
        if is_new and not self.merchant_trade_no:
            super().save(*args, **kwargs)
            self.merchant_trade_no = f"{self.id}{uuid.uuid4().hex[:6].upper()}"
            kwargs['force_insert'] = False
            # 繼續往下走，會在末尾再 save 一次

        # 狀態變更處理（僅更新時）
        if not is_new and self._original_status != self.status:
            from django.utils import timezone

            if self._original_status != self.STATUS_PAID and self.status == self.STATUS_PAID:
                # 從未付款 → 已付款
                if not self.paid_at:
                    self.paid_at = timezone.now()
            elif self._original_status == self.STATUS_PAID and self.status != self.STATUS_PAID:
                # 從已付款 → 其他狀態
                self.paid_at = None

        super().save(*args, **kwargs)

        # 狀態變更後更新銷售統計
        if not is_new and self._original_status != self.status:
            if (self._original_status != self.STATUS_PAID and self.status == self.STATUS_PAID) or \
               (self._original_status == self.STATUS_PAID and self.status != self.STATUS_PAID):
                for item in self.items.all():
                    item.product.update_sales_count()

        # 更新暫存狀態
        self._original_status = self.status

    def __str__(self):
        return f"Order {self.id} by {self.user.email}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def get_total(self):
        """計算該項目的總價 (數量 x 單價)"""
        return self.quantity * self.price

    @property
    def total(self):
        """總價的屬性方式訪問"""
        return self.get_total()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # 移除自動更新銷售統計 - 應該在付款完成後才計算
        # self.product.update_sales_count()

    def delete(self, *args, **kwargs):
        product = self.product
        super().delete(*args, **kwargs)
        # 如果該訂單已付款，需要減少銷售統計
        if self.order.status == Order.STATUS_PAID:
            product.update_sales_count()

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
