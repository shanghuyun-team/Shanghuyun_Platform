from functools import wraps

from django.shortcuts import redirect, render

from .models import MonitoringPermission


def monitoring_permission_required(view_func):
    """
    Decorator：檢查使用者是否已登入且擁有生產監控權限。
    - 未登入 → redirect 到登入頁
    - 已登入但無權限 → 顯示 no_permission 頁面
    """

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.conf import settings as django_settings
            login_url = getattr(django_settings, "LOGIN_URL", "/accounts/login/")
            return redirect(f"{login_url}?next={request.path}")

        # 超級管理員直接放行
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        try:
            perm = MonitoringPermission.objects.get(user=request.user)
            if perm.is_enabled:
                return view_func(request, *args, **kwargs)
        except MonitoringPermission.DoesNotExist:
            pass

        return render(request, "monitoring/no_permission.html", status=403)

    return _wrapped
