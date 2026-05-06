import json

from django.test import TestCase, Client
from django.urls import reverse

from api.v1.account.models import User
from apps.monitoring.models import MonitoringPermission, Sensor, SensorReading


class MonitoringTestBase(TestCase):
    """測試基底 — 建立共用的測試使用者、感測器等"""

    def setUp(self):
        # 一般使用者（有權限）
        self.user = User.objects.create_user(
            email="farmer@test.com", password="testpass123"
        )
        self.perm = MonitoringPermission.objects.create(
            user=self.user, is_enabled=True
        )

        # 另一個使用者
        self.other_user = User.objects.create_user(
            email="other@test.com", password="testpass123"
        )
        MonitoringPermission.objects.create(
            user=self.other_user, is_enabled=True
        )

        # 未授權使用者
        self.no_perm_user = User.objects.create_user(
            email="noperm@test.com", password="testpass123"
        )

        # 超級管理員
        self.admin = User.objects.create_superuser(
            email="admin@test.com", password="adminpass123"
        )

        # 建立感測器
        self.sensor = Sensor.objects.create(
            owner=self.user,
            name="溫室溫度",
            sensor_type="temperature",
            location="溫室 A",
            unit="°C",
        )
        self.other_sensor = Sensor.objects.create(
            owner=self.other_user,
            name="他人的感測器",
            sensor_type="humidity",
            unit="%",
        )

        self.client = Client()


class AccessControlTests(MonitoringTestBase):
    """測試存取控制"""

    def test_unauthenticated_redirect(self):
        """未登入使用者 → redirect 到登入頁"""
        response = self.client.get(reverse("monitoring:dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_unauthorized_user_gets_403(self):
        """已登入但未授權 → 403"""
        self.client.login(email="noperm@test.com", password="testpass123")
        response = self.client.get(reverse("monitoring:dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_authorized_user_dashboard(self):
        """已授權使用者可進入儀表板"""
        self.client.login(email="farmer@test.com", password="testpass123")
        response = self.client.get(reverse("monitoring:dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_superuser_bypass(self):
        """超級管理員無需 MonitoringPermission"""
        self.client.login(email="admin@test.com", password="adminpass123")
        response = self.client.get(reverse("monitoring:dashboard"))
        self.assertEqual(response.status_code, 200)


class DataIsolationTests(MonitoringTestBase):
    """測試資料隔離"""

    def test_sensor_list_only_own(self):
        """使用者只能看到自己的感測器"""
        self.client.login(email="farmer@test.com", password="testpass123")
        response = self.client.get(reverse("monitoring:sensor_list"))
        self.assertContains(response, "溫室溫度")
        self.assertNotContains(response, "他人的感測器")

    def test_cannot_view_others_sensor(self):
        """不能透過 URL 查看他人的感測器"""
        self.client.login(email="farmer@test.com", password="testpass123")
        response = self.client.get(
            reverse("monitoring:sensor_detail", args=[self.other_sensor.pk])
        )
        self.assertEqual(response.status_code, 404)

    def test_cannot_edit_others_sensor(self):
        """不能編輯他人的感測器"""
        self.client.login(email="farmer@test.com", password="testpass123")
        response = self.client.get(
            reverse("monitoring:sensor_edit", args=[self.other_sensor.pk])
        )
        self.assertEqual(response.status_code, 404)

    def test_cannot_delete_others_sensor(self):
        """不能刪除他人的感測器"""
        self.client.login(email="farmer@test.com", password="testpass123")
        response = self.client.post(
            reverse("monitoring:sensor_delete", args=[self.other_sensor.pk])
        )
        self.assertEqual(response.status_code, 404)


class SensorCRUDTests(MonitoringTestBase):
    """測試感測器 CRUD"""

    def test_create_sensor_auto_owner(self):
        """建立感測器時 owner 自動設為登入者"""
        self.client.login(email="farmer@test.com", password="testpass123")
        response = self.client.post(reverse("monitoring:sensor_create"), {
            "name": "新感測器",
            "sensor_type": "humidity",
            "unit": "%",
            "is_active": True,
        })
        self.assertEqual(response.status_code, 302)  # redirect after success
        sensor = Sensor.objects.get(name="新感測器")
        self.assertEqual(sensor.owner, self.user)
        self.assertTrue(len(sensor.api_key) > 0)

    def test_delete_sensor(self):
        """可以刪除自己的感測器"""
        self.client.login(email="farmer@test.com", password="testpass123")
        response = self.client.post(
            reverse("monitoring:sensor_delete", args=[self.sensor.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Sensor.objects.filter(pk=self.sensor.pk).exists())


class APITests(MonitoringTestBase):
    """測試感測器資料上傳 API"""

    def test_valid_api_key_creates_reading(self):
        """有效 api_key → 201"""
        response = self.client.post(
            reverse("monitoring_create_reading"),
            data=json.dumps({
                "api_key": self.sensor.api_key,
                "value": 25.5,
            }),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(SensorReading.objects.count(), 1)

    def test_invalid_api_key(self):
        """無效 api_key → 403"""
        response = self.client.post(
            reverse("monitoring_create_reading"),
            data=json.dumps({
                "api_key": "invalid_key_12345",
                "value": 10,
            }),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_inactive_sensor_rejected(self):
        """停用的感測器 → 403"""
        self.sensor.is_active = False
        self.sensor.save()
        response = self.client.post(
            reverse("monitoring_create_reading"),
            data=json.dumps({
                "api_key": self.sensor.api_key,
                "value": 10,
            }),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_missing_value(self):
        """缺少 value → 400"""
        response = self.client.post(
            reverse("monitoring_create_reading"),
            data=json.dumps({
                "api_key": self.sensor.api_key,
            }),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_with_recorded_at(self):
        """可指定 recorded_at"""
        response = self.client.post(
            reverse("monitoring_create_reading"),
            data=json.dumps({
                "api_key": self.sensor.api_key,
                "value": 22.3,
                "recorded_at": "2026-01-15T10:30:00+08:00",
            }),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        reading = SensorReading.objects.first()
        self.assertEqual(float(reading.value), 22.3)

    def test_with_raw_data(self):
        """可附加 raw_data"""
        response = self.client.post(
            reverse("monitoring_create_reading"),
            data=json.dumps({
                "api_key": self.sensor.api_key,
                "value": 30,
                "raw_data": {"battery": 85, "rssi": -45},
            }),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        reading = SensorReading.objects.first()
        self.assertEqual(reading.raw_data["battery"], 85)
