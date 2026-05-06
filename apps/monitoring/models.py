import secrets

from django.conf import settings
from django.db import models


class MonitoringPermission(models.Model):
    """使用者監控權限 — 控制哪些使用者可以使用生產監控功能"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="monitoring_permission",
        verbose_name="使用者",
    )
    is_enabled = models.BooleanField(
        "啟用生產監控",
        default=True,
        help_text="勾選後該使用者即可使用生產監控功能",
    )
    created_at = models.DateTimeField("建立時間", auto_now_add=True)
    updated_at = models.DateTimeField("更新時間", auto_now=True)

    class Meta:
        verbose_name = "監控權限"
        verbose_name_plural = "監控權限"

    def __str__(self):
        status = "✓" if self.is_enabled else "✗"
        return f"{self.user.email} [{status}]"


class Sensor(models.Model):
    """感測器 — 每位使用者可建立自己的感測器"""

    SENSOR_TYPE_CHOICES = [
        ("temperature", "溫度"),
        ("humidity", "濕度"),
        ("soil_moisture", "土壤濕度"),
        ("light", "光照"),
        ("ph", "pH"),
        ("ec", "EC"),
        ("other", "其他"),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sensors",
        verbose_name="擁有者",
    )
    name = models.CharField("感測器名稱", max_length=200)
    sensor_type = models.CharField(
        "感測器類型",
        max_length=20,
        choices=SENSOR_TYPE_CHOICES,
        default="temperature",
    )
    location = models.CharField("安裝位置", max_length=255, blank=True)
    description = models.TextField("備註", blank=True)
    unit = models.CharField(
        "數值單位",
        max_length=20,
        blank=True,
        help_text="例如：°C、%、lux、pH",
    )
    api_key = models.CharField(
        "API Key",
        max_length=64,
        unique=True,
        editable=False,
        help_text="感測器上傳資料用的識別金鑰（自動產生）",
    )
    is_active = models.BooleanField("是否啟用", default=True)
    created_at = models.DateTimeField("建立時間", auto_now_add=True)
    updated_at = models.DateTimeField("更新時間", auto_now=True)

    class Meta:
        verbose_name = "感測器"
        verbose_name_plural = "感測器"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.get_sensor_type_display()})"

    def save(self, *args, **kwargs):
        if not self.api_key:
            self.api_key = secrets.token_hex(32)
        super().save(*args, **kwargs)

    @property
    def latest_reading(self):
        """取得最新的感測數據"""
        return self.readings.order_by("-recorded_at").first()


class SensorReading(models.Model):
    """感測數據 — 儲存感測器上傳的數值"""

    sensor = models.ForeignKey(
        Sensor,
        on_delete=models.CASCADE,
        related_name="readings",
        verbose_name="感測器",
    )
    value = models.DecimalField(
        "感測數值",
        max_digits=12,
        decimal_places=4,
    )
    recorded_at = models.DateTimeField("資料紀錄時間", db_index=True)
    raw_data = models.JSONField("原始資料", null=True, blank=True)
    created_at = models.DateTimeField("建立時間", auto_now_add=True)

    class Meta:
        verbose_name = "感測數據"
        verbose_name_plural = "感測數據"
        ordering = ["-recorded_at"]
        indexes = [
            models.Index(fields=["sensor", "-recorded_at"]),
        ]

    def __str__(self):
        return f"{self.sensor.name}: {self.value} @ {self.recorded_at}"
