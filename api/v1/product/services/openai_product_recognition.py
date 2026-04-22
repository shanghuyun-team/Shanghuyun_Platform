"""
OpenAI 商品圖片辨識 Service
=============================
透過 OpenAI Responses API 分析商品圖片，回傳商品名稱、建議售價、商品描述。

所有 OpenAI 設定從 Django settings（環境變數）讀取：
- OPENAI_API_KEY
- OPENAI_MODEL
- OPENAI_TIMEOUT
"""

import base64
import json
import logging
import mimetypes

from django.conf import settings
from openai import OpenAI, APIError, APITimeoutError, APIConnectionError

logger = logging.getLogger(__name__)

# ── 最大描述長度 ──────────────────────────────────
MAX_DESCRIPTION_LENGTH = 500


def _get_client() -> OpenAI:
    """建立 OpenAI client，從 settings 讀取設定。"""
    api_key = getattr(settings, "OPENAI_API_KEY", "")
    if not api_key:
        raise ValueError("OPENAI_API_KEY 尚未設定，請在 .env 中填入有效的 API Key。")
    timeout = getattr(settings, "OPENAI_TIMEOUT", 30)
    return OpenAI(api_key=api_key, timeout=timeout)


def _image_to_data_url(image) -> str:
    """
    將 Wagtail Image 物件轉為 Base64 data URL。

    Parameters
    ----------
    image : wagtail.images.models.Image
        Wagtail 圖片物件

    Returns
    -------
    str
        data:image/xxx;base64,... 格式的字串
    """
    file_obj = image.file
    file_obj.open("rb")
    try:
        raw_bytes = file_obj.read()
    finally:
        file_obj.close()

    # 從檔名判斷 MIME type
    mime_type, _ = mimetypes.guess_type(file_obj.name or "image.jpg")
    if not mime_type or not mime_type.startswith("image/"):
        mime_type = "image/jpeg"

    b64 = base64.b64encode(raw_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{b64}"


# ── Prompt ────────────────────────────────────────
SYSTEM_PROMPT = """你是一位專業的商品辨識助手。使用者會上傳一張商品圖片，請你辨識圖片中的商品並回傳以下資訊。

# 回傳規則
1. 只回傳 JSON，不要回傳 Markdown、不要回傳額外說明文字。
2. JSON 結構如下：
{
  "product_name": "商品名稱（繁體中文）",
  "suggested_price": 123,
  "description": "商品描述（繁體中文）",
  "confidence": 0.85,
  "needs_review": false
}

# 各欄位說明
- product_name: 商品名稱，繁體中文，簡潔明確。不可為空字串。
- suggested_price: 建議售價（新台幣整數），根據常見市場售價給合理估計。不可為負數或零。若無法判斷，給保守估計並將 needs_review 設為 true。
- description: 商品描述，繁體中文，風格自然簡潔，適合用在商品頁簡介。避免誇大、避免醫療或違規宣稱。長度不超過 300 字。
- confidence: 辨識信心度 0.0~1.0。若圖片模糊、商品不明確，請降低信心度。
- needs_review: 布林值。若信心度低於 0.7 或價格難以判斷，設為 true。

# 價格判斷原則
- 依常見市場區間給保守估計
- 不可給出非常誇張的價格
- 若信心不足，needs_review = true

# 重要
- 若圖片不是商品圖片（例如風景照、人物照、截圖等），仍嘗試描述，但 confidence 設低、needs_review 設為 true。
"""

USER_PROMPT = "請辨識這張商品圖片，並回傳 JSON 格式的商品資訊。"


def recognize_product(image) -> dict:
    """
    使用 OpenAI Responses API 辨識商品圖片。

    Parameters
    ----------
    image : wagtail.images.models.Image
        Wagtail 圖片物件

    Returns
    -------
    dict
        包含 product_name, suggested_price, description, confidence, needs_review

    Raises
    ------
    ValueError
        設定錯誤、回傳格式錯誤、驗證失敗
    ConnectionError
        API 連線或超時錯誤
    RuntimeError
        其他 API 錯誤
    """
    model_name = getattr(settings, "OPENAI_MODEL", "gpt-4o")
    logger.info("開始辨識商品圖片 image_id=%s，使用模型 %s", image.pk, model_name)

    # 1. 圖片轉 Base64 data URL
    try:
        data_url = _image_to_data_url(image)
    except Exception as e:
        logger.error("圖片讀取失敗 image_id=%s: %s", image.pk, e)
        raise ValueError(f"圖片讀取失敗：{e}")

    # 2. 呼叫 OpenAI Responses API
    client = _get_client()
    try:
        response = client.responses.create(
            model=model_name,
            input=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": USER_PROMPT},
                        {
                            "type": "input_image",
                            "image_url": data_url,
                        },
                    ],
                },
            ],
        )
    except APITimeoutError as e:
        logger.error("OpenAI API 超時 image_id=%s: %s", image.pk, e)
        raise ConnectionError(f"OpenAI API 請求超時，請稍後再試。")
    except APIConnectionError as e:
        logger.error("OpenAI API 連線失敗 image_id=%s: %s", image.pk, e)
        raise ConnectionError(f"無法連線至 OpenAI API，請檢查網路或 API 設定。")
    except APIError as e:
        logger.error("OpenAI API 錯誤 image_id=%s: %s", image.pk, e)
        raise RuntimeError(f"OpenAI API 錯誤：{e.message}")

    # 3. 解析回傳
    try:
        raw_text = response.output_text
        logger.debug("OpenAI 原始回傳: %s", raw_text)
    except (AttributeError, IndexError) as e:
        logger.error("無法取得 OpenAI 回傳文字 image_id=%s: %s", image.pk, e)
        raise RuntimeError("OpenAI 回傳格式異常，無法取得回應文字。")

    # 嘗試清理可能的 markdown code block 包裹
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        # 移除 ```json ... ``` 包裹
        lines = cleaned.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines)

    try:
        result = json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error("OpenAI 回傳 JSON 解析失敗 image_id=%s: %s\n原始內容: %s", image.pk, e, raw_text)
        raise ValueError(f"AI 回傳格式錯誤，無法解析為 JSON。請重試。")

    # 4. 驗證欄位
    result = _validate_result(result, image.pk)

    logger.info(
        "商品辨識完成 image_id=%s: name=%s, price=%s, confidence=%s, needs_review=%s",
        image.pk, result["product_name"], result["suggested_price"],
        result["confidence"], result["needs_review"],
    )
    return result


def _validate_result(result: dict, image_id) -> dict:
    """
    驗證並清理 OpenAI 回傳的辨識結果。

    - product_name: 不可為空
    - suggested_price: 必須為正數
    - description: 截斷過長內容
    - confidence: 0.0 ~ 1.0
    - needs_review: bool
    """
    # product_name
    name = result.get("product_name", "").strip()
    if not name:
        logger.warning("product_name 為空 image_id=%s，標記需人工確認", image_id)
        name = "（待填寫）"
        result["needs_review"] = True
    result["product_name"] = name

    # suggested_price
    try:
        price = result.get("suggested_price", 0)
        price = int(float(price))
        if price <= 0:
            logger.warning("suggested_price <= 0 image_id=%s，設為 0 並標記需人工確認", image_id)
            price = 0
            result["needs_review"] = True
    except (TypeError, ValueError):
        logger.warning("suggested_price 無法轉為數字 image_id=%s，設為 0", image_id)
        price = 0
        result["needs_review"] = True
    result["suggested_price"] = price

    # description
    desc = result.get("description", "").strip()
    if len(desc) > MAX_DESCRIPTION_LENGTH:
        logger.info("description 過長 (%d chars)，截斷至 %d image_id=%s", len(desc), MAX_DESCRIPTION_LENGTH, image_id)
        desc = desc[:MAX_DESCRIPTION_LENGTH] + "…"
    result["description"] = desc

    # confidence
    try:
        conf = float(result.get("confidence", 0.0))
        conf = max(0.0, min(1.0, conf))
    except (TypeError, ValueError):
        conf = 0.0
    result["confidence"] = conf

    # needs_review
    needs_review = result.get("needs_review", False)
    if not isinstance(needs_review, bool):
        needs_review = bool(needs_review)
    # 信心度低於 0.7 強制需要審核
    if conf < 0.7:
        needs_review = True
    result["needs_review"] = needs_review

    return result
