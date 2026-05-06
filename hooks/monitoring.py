from wagtail_modeladmin.options import ModelAdmin, modeladmin_register
from wagtail_modeladmin.helpers import PermissionHelper

from apps.monitoring.models import MonitoringPermission, Sensor, SensorReading


class SuperuserOnlyPermission(PermissionHelper):
    def user_can_list(self, user):
        return user.is_superuser
    def user_can_create(self, user):
        return user.is_superuser
    def user_can_edit_obj(self, user, obj):
        return user.is_superuser
    def user_can_delete_obj(self, user, obj):
        return user.is_superuser


class MonitoringPermissionAdmin(ModelAdmin):
    model = MonitoringPermission
    menu_label = "監控權限"
    menu_icon = "lock"
    permission_helper_class = SuperuserOnlyPermission
    list_display = ("user", "is_enabled", "created_at", "updated_at")
    search_fields = ("user__email",)
    list_filter = ("is_enabled",)

modeladmin_register(MonitoringPermissionAdmin)


class SensorAdmin(ModelAdmin):
    model = Sensor
    menu_label = "感測器管理"
    menu_icon = "cog"
    permission_helper_class = SuperuserOnlyPermission
    list_display = (
        "name", "owner", "sensor_type", "location",
        "is_active", "created_at", "latest_reading_time",
    )
    search_fields = ("name", "owner__email", "location")
    list_filter = ("sensor_type", "is_active")

    def latest_reading_time(self, obj):
        reading = obj.latest_reading
        if reading:
            return reading.recorded_at.strftime("%Y/%m/%d %H:%M")
        return "—"
    latest_reading_time.short_description = "最新資料時間"

modeladmin_register(SensorAdmin)


class SensorReadingAdmin(ModelAdmin):
    model = SensorReading
    menu_label = "感測數據"
    menu_icon = "doc-full"
    permission_helper_class = SuperuserOnlyPermission
    list_display = ("sensor", "value", "recorded_at", "created_at")
    search_fields = ("sensor__name",)
    list_filter = ("sensor",)

modeladmin_register(SensorReadingAdmin)
