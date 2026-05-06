import logging

from django.contrib import messages
from django.db.models import Avg, Max, Min
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .decorators import monitoring_permission_required
from .forms import SensorForm
from .models import Sensor, SensorReading

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 儀表板
# ---------------------------------------------------------------------------

@monitoring_permission_required
def dashboard(request):
    """生產監控儀表板"""
    sensors = Sensor.objects.filter(owner=request.user)
    total_sensors = sensors.count()
    active_sensors = sensors.filter(is_active=True).count()

    # 最近更新的感測器（取最新 5 筆 reading 對應的 sensor）
    recent_readings = (
        SensorReading.objects
        .filter(sensor__owner=request.user)
        .select_related("sensor")
        .order_by("-recorded_at")[:10]
    )

    context = {
        "total_sensors": total_sensors,
        "active_sensors": active_sensors,
        "inactive_sensors": total_sensors - active_sensors,
        "recent_readings": recent_readings,
        "sensors": sensors.filter(is_active=True)[:10],
    }
    return render(request, "monitoring/dashboard.html", context)


# ---------------------------------------------------------------------------
# 感測器 CRUD
# ---------------------------------------------------------------------------

@monitoring_permission_required
def sensor_list(request):
    """感測器列表（僅自己的）"""
    sensors = Sensor.objects.filter(owner=request.user)
    return render(request, "monitoring/sensor_list.html", {"sensors": sensors})


@monitoring_permission_required
def sensor_create(request):
    """新增感測器"""
    if request.method == "POST":
        form = SensorForm(request.POST)
        if form.is_valid():
            sensor = form.save(commit=False)
            sensor.owner = request.user
            sensor.save()
            messages.success(request, f"感測器「{sensor.name}」已建立。")
            return redirect("monitoring:sensor_detail", pk=sensor.pk)
    else:
        form = SensorForm()
    return render(request, "monitoring/sensor_form.html", {
        "form": form,
        "is_edit": False,
    })


@monitoring_permission_required
def sensor_detail(request, pk):
    """感測器詳情 + 圖表"""
    sensor = get_object_or_404(Sensor, pk=pk, owner=request.user)
    recent_readings = sensor.readings.order_by("-recorded_at")[:20]
    return render(request, "monitoring/sensor_detail.html", {
        "sensor": sensor,
        "recent_readings": recent_readings,
    })


@monitoring_permission_required
def sensor_edit(request, pk):
    """編輯感測器"""
    sensor = get_object_or_404(Sensor, pk=pk, owner=request.user)
    if request.method == "POST":
        form = SensorForm(request.POST, instance=sensor)
        if form.is_valid():
            form.save()
            messages.success(request, f"感測器「{sensor.name}」已更新。")
            return redirect("monitoring:sensor_detail", pk=sensor.pk)
    else:
        form = SensorForm(instance=sensor)
    return render(request, "monitoring/sensor_form.html", {
        "form": form,
        "sensor": sensor,
        "is_edit": True,
    })


@monitoring_permission_required
def sensor_delete(request, pk):
    """刪除感測器（需 POST 確認）"""
    sensor = get_object_or_404(Sensor, pk=pk, owner=request.user)
    if request.method == "POST":
        name = sensor.name
        sensor.delete()
        messages.success(request, f"感測器「{name}」已刪除。")
        return redirect("monitoring:sensor_list")
    return render(request, "monitoring/sensor_confirm_delete.html", {
        "sensor": sensor,
    })


# ---------------------------------------------------------------------------
# 圖表資料 JSON endpoint
# ---------------------------------------------------------------------------

@monitoring_permission_required
def sensor_data_api(request, pk):
    """回傳感測器圖表資料（JSON），供 Chart.js 使用"""
    sensor = get_object_or_404(Sensor, pk=pk, owner=request.user)

    # 時間範圍：24h / 7d / 30d
    range_param = request.GET.get("range", "24h")
    now = timezone.now()
    if range_param == "7d":
        since = now - timezone.timedelta(days=7)
    elif range_param == "30d":
        since = now - timezone.timedelta(days=30)
    else:
        since = now - timezone.timedelta(hours=24)

    readings = (
        sensor.readings
        .filter(recorded_at__gte=since)
        .order_by("recorded_at")
        .values_list("recorded_at", "value")
    )

    labels = []
    values = []
    for ts, val in readings:
        local_ts = timezone.localtime(ts)
        if range_param == "24h":
            labels.append(local_ts.strftime("%H:%M"))
        else:
            labels.append(local_ts.strftime("%m/%d %H:%M"))
        values.append(float(val))

    return JsonResponse({
        "labels": labels,
        "values": values,
        "sensor_name": sensor.name,
        "unit": sensor.unit,
        "range": range_param,
    })


# ---------------------------------------------------------------------------
# AI 即時建議
# ---------------------------------------------------------------------------

def _build_sensor_stats(sensor):
    """彙整單一感測器的 24 小時統計資料"""
    now = timezone.now()
    since_24h = now - timezone.timedelta(hours=24)

    readings_24h = sensor.readings.filter(recorded_at__gte=since_24h)
    stats = readings_24h.aggregate(
        avg=Avg("value"),
        min_val=Min("value"),
        max_val=Max("value"),
    )

    latest = sensor.latest_reading
    count = readings_24h.count()

    # 計算簡單趨勢：比較前半段與後半段的平均值
    trend = "unknown"
    if count >= 4:
        mid = since_24h + (now - since_24h) / 2
        first_half_avg = readings_24h.filter(recorded_at__lt=mid).aggregate(a=Avg("value"))["a"]
        second_half_avg = readings_24h.filter(recorded_at__gte=mid).aggregate(a=Avg("value"))["a"]
        if first_half_avg is not None and second_half_avg is not None:
            diff = float(second_half_avg - first_half_avg)
            if abs(diff) < 0.5:
                trend = "stable"
            elif diff > 0:
                trend = "up"
            else:
                trend = "down"

    return {
        "name": sensor.name,
        "sensor_type": sensor.get_sensor_type_display(),
        "unit": sensor.unit or "",
        "latest_value": float(latest.value) if latest else None,
        "avg_24h": float(stats["avg"]) if stats["avg"] is not None else None,
        "min_24h": float(stats["min_val"]) if stats["min_val"] is not None else None,
        "max_24h": float(stats["max_val"]) if stats["max_val"] is not None else None,
        "reading_count_24h": count,
        "trend": trend,
    }


@monitoring_permission_required
def ai_recommendation(request):
    """
    GET /monitoring/ai-recommendation/
    回傳所有啟用中感測器的 AI 綜合建議（JSON）
    """
    sensors = Sensor.objects.filter(owner=request.user, is_active=True)
    sensors_data = [_build_sensor_stats(s) for s in sensors]

    try:
        from .services import get_ai_recommendation
        result = get_ai_recommendation(sensors_data)
    except ValueError as e:
        logger.error("AI 建議 ValueError: %s", e)
        return JsonResponse({"error": str(e)}, status=400)
    except ConnectionError as e:
        logger.error("AI 建議 ConnectionError: %s", e)
        return JsonResponse({"error": str(e)}, status=503)
    except RuntimeError as e:
        logger.error("AI 建議 RuntimeError: %s", e)
        return JsonResponse({"error": str(e)}, status=502)
    except Exception as e:
        logger.exception("AI 建議未預期錯誤: %s", e)
        return JsonResponse({"error": "AI 分析過程發生錯誤，請稍後再試。"}, status=500)

    return JsonResponse({"success": True, "data": result})


@monitoring_permission_required
def ai_sensor_recommendation(request, pk):
    """
    GET /monitoring/sensors/<pk>/ai-recommendation/
    回傳單一感測器的 AI 建議（JSON）
    """
    sensor = get_object_or_404(Sensor, pk=pk, owner=request.user)
    sensor_data = _build_sensor_stats(sensor)

    try:
        from .services import get_sensor_recommendation
        result = get_sensor_recommendation(sensor_data)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except ConnectionError as e:
        return JsonResponse({"error": str(e)}, status=503)
    except RuntimeError as e:
        return JsonResponse({"error": str(e)}, status=502)
    except Exception as e:
        logger.exception("AI sensor 建議錯誤: %s", e)
        return JsonResponse({"error": "AI 分析過程發生錯誤，請稍後再試。"}, status=500)

    return JsonResponse({"success": True, "data": result})
