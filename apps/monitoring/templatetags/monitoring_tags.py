from django import template

register = template.Library()


@register.simple_tag
def has_monitoring_permission(user):
    """
    檢查使用者是否有生產監控權限。
    用法：{% has_monitoring_permission user as can_monitor %}
    """
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    try:
        return user.monitoring_permission.is_enabled
    except Exception:
        return False
