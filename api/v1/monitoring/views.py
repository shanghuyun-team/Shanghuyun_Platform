import json

from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.monitoring.models import Sensor, SensorReading


@csrf_exempt
@require_POST
def create_reading(request):
    """
    感測器資料上傳 API

    POST /api/v1/monitoring/readings/
    Content-Type: application/json

    {
        "api_key": "...",
        "value": 25.5,
        "recorded_at": "2026-01-01T12:00:00Z",  // 可選
        "raw_data": {...}                         // 可選
    }
    """
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse(
            {"error": "請求格式錯誤，需為 JSON。"},
            status=400,
        )

    api_key = data.get("api_key")
    if not api_key:
        return JsonResponse(
            {"error": "缺少 api_key 欄位。"},
            status=400,
        )

    # 查找感測器
    try:
        sensor = Sensor.objects.get(api_key=api_key)
    except Sensor.DoesNotExist:
        return JsonResponse(
            {"error": "無效的 api_key，找不到對應的感測器。"},
            status=403,
        )

    # 確認啟用
    if not sensor.is_active:
        return JsonResponse(
            {"error": "此感測器已停用，無法接收資料。"},
            status=403,
        )

    # 取得數值
    value = data.get("value")
    if value is None:
        return JsonResponse(
            {"error": "缺少 value 欄位。"},
            status=400,
        )

    try:
        value = float(value)
    except (TypeError, ValueError):
        return JsonResponse(
            {"error": "value 必須為數值。"},
            status=400,
        )

    # 紀錄時間
    recorded_at_str = data.get("recorded_at")
    if recorded_at_str:
        from django.utils.dateparse import parse_datetime
        recorded_at = parse_datetime(recorded_at_str)
        if recorded_at is None:
            return JsonResponse(
                {"error": "recorded_at 格式無效，請使用 ISO 8601 格式。"},
                status=400,
            )
        if timezone.is_naive(recorded_at):
            recorded_at = timezone.make_aware(recorded_at)
    else:
        recorded_at = timezone.now()

    # 原始資料
    raw_data = data.get("raw_data")

    # 建立 SensorReading
    reading = SensorReading.objects.create(
        sensor=sensor,
        value=value,
        recorded_at=recorded_at,
        raw_data=raw_data,
    )

    return JsonResponse(
        {
            "success": True,
            "reading_id": reading.pk,
            "sensor": sensor.name,
            "value": float(reading.value),
            "recorded_at": reading.recorded_at.isoformat(),
        },
        status=201,
    )
