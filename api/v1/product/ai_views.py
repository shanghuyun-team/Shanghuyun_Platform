"""
AI 商品辨識 AJAX Endpoint
==========================
提供給 Wagtail admin 前端呼叫的 API view。
接收 image_id，呼叫 OpenAI service 辨識後回傳 JSON。
"""

import json
import logging

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from wagtail.images.models import Image

from .services.openai_product_recognition import recognize_product

logger = logging.getLogger(__name__)


@login_required
@require_POST
def ai_recognize_view(request):
    """
    POST /admin/product/ai-recognize/
    Body: {"image_id": 123}

    權限：需登入且為 staff / superuser / vendor
    """
    user = request.user

    # ── 權限檢查 ──
    has_permission = (
        user.is_superuser
        or user.is_staff
        or getattr(user, "is_vendor", False)
    )
    if not has_permission:
        logger.warning("AI 辨識權限不足 user=%s", user.pk)
        return JsonResponse(
            {"error": "您沒有使用此功能的權限。"},
            status=403,
        )

    # ── 解析請求 ──
    try:
        body = json.loads(request.body)
        image_id = body.get("image_id")
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({"error": "請求格式錯誤，預期 JSON body。"}, status=400)

    if not image_id:
        return JsonResponse({"error": "缺少 image_id 參數。"}, status=400)

    # ── 取得圖片 ──
    try:
        image = Image.objects.get(pk=image_id)
    except Image.DoesNotExist:
        return JsonResponse({"error": f"找不到圖片 (ID: {image_id})。"}, status=404)

    # ── 呼叫 OpenAI Service ──
    try:
        result = recognize_product(image)
    except ValueError as e:
        logger.error("AI 辨識 ValueError: %s", e)
        return JsonResponse({"error": str(e)}, status=400)
    except ConnectionError as e:
        logger.error("AI 辨識 ConnectionError: %s", e)
        return JsonResponse({"error": str(e)}, status=503)
    except RuntimeError as e:
        logger.error("AI 辨識 RuntimeError: %s", e)
        return JsonResponse({"error": str(e)}, status=502)
    except Exception as e:
        logger.exception("AI 辨識未預期錯誤: %s", e)
        return JsonResponse({"error": "辨識過程發生未預期錯誤，請稍後再試。"}, status=500)

    return JsonResponse({"success": True, "data": result})
