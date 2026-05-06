"""
AI 感測器數據分析建議 Service
================================
利用 OpenAI API 分析感測器數據，提供即時農業生產建議。
"""

import json
import logging

from django.conf import settings
from openai import OpenAI, APIError, APITimeoutError, APIConnectionError

logger = logging.getLogger(__name__)


def _get_client() -> OpenAI:
    """建立 OpenAI client，從 settings 讀取設定。"""
    api_key = getattr(settings, "OPENAI_API_KEY", "")
    if not api_key:
        raise ValueError("OPENAI_API_KEY 尚未設定，請在 .env 中填入有效的 API Key。")
    timeout = getattr(settings, "OPENAI_TIMEOUT", 30)
    return OpenAI(api_key=api_key, timeout=timeout)


# ── Prompt ────────────────────────────────────────
SYSTEM_PROMPT = """你是一位專業的智慧農業顧問，專精於分析農場感測器數據並提供生產管理建議。

# 角色
你會收到農場感測器的即時數據與歷史摘要，需要根據這些數據提供：
1. 目前環境狀態的整體評估
2. 異常指標的警告
3. 具體可行的農業管理建議
4. 根據趨勢的預測與預防措施

# 回傳規則
1. 只回傳 JSON，不要回傳 Markdown、不要回傳額外說明文字。
2. JSON 結構如下：
{
  "overall_status": "良好|注意|警告|危險",
  "status_color": "green|yellow|orange|red",
  "summary": "一段 50 字以內的整體摘要",
  "alerts": [
    {
      "level": "info|warning|danger",
      "sensor_name": "感測器名稱",
      "message": "警告內容"
    }
  ],
  "recommendations": [
    {
      "title": "建議標題",
      "description": "具體建議內容（繁體中文，自然簡潔）",
      "priority": "high|medium|low",
      "category": "irrigation|temperature|fertilizer|pest|general"
    }
  ],
  "trends": "簡短描述數據趨勢（50 字以內）"
}

# 判斷原則
- 溫度: 適宜範圍 15-35°C，過高或過低需警告
- 濕度: 適宜範圍 40-80%，太低需灌溉、太高需通風
- 土壤濕度: 適宜範圍 30-70%，太低需灌溉
- 光照: 依作物而異，一般 5000-50000 lux
- pH: 適宜範圍 5.5-7.5
- EC: 適宜範圍 0.5-3.0 mS/cm
- 若資料不足或無法判斷，仍給出通用建議，不要回傳空陣列

# 重要
- 回覆使用繁體中文
- 建議必須具體可行，不要使用模糊語句
- 若資料點很少，提醒使用者需要更多數據才能做出準確判斷
- 至少給出 1-3 條建議
"""


def get_ai_recommendation(sensors_data: list[dict]) -> dict:
    """
    分析感測器數據，回傳 AI 建議。

    Parameters
    ----------
    sensors_data : list[dict]
        每個 dict 包含：
        - name: 感測器名稱
        - sensor_type: 類型 (temperature/humidity/...)
        - unit: 單位
        - latest_value: 最新數值 (float or None)
        - avg_24h: 24 小時平均 (float or None)
        - min_24h: 24 小時最低 (float or None)
        - max_24h: 24 小時最高 (float or None)
        - reading_count_24h: 24 小時內資料筆數
        - trend: "up" | "down" | "stable" | "unknown"

    Returns
    -------
    dict
        AI 分析結果

    Raises
    ------
    ValueError, ConnectionError, RuntimeError
    """
    model_name = getattr(settings, "OPENAI_MODEL", "gpt-4o")
    logger.info("開始 AI 感測數據分析，使用模型 %s，感測器數量 %d", model_name, len(sensors_data))

    # 構建使用者 prompt
    if not sensors_data:
        user_content = "目前沒有感測器資料，請給出一般性的農業生產建議。"
    else:
        lines = ["以下是農場感測器的即時數據：\n"]
        for s in sensors_data:
            line = f"【{s['name']}】 類型={s['sensor_type']}, 單位={s['unit']}"
            if s.get("latest_value") is not None:
                line += f", 最新值={s['latest_value']}"
            if s.get("avg_24h") is not None:
                line += f", 24h平均={s['avg_24h']:.1f}"
            if s.get("min_24h") is not None:
                line += f", 24h最低={s['min_24h']:.1f}"
            if s.get("max_24h") is not None:
                line += f", 24h最高={s['max_24h']:.1f}"
            line += f", 24h資料筆數={s.get('reading_count_24h', 0)}"
            line += f", 趨勢={s.get('trend', 'unknown')}"
            lines.append(line)
        lines.append("\n請分析以上數據，並提供農業生產建議。")
        user_content = "\n".join(lines)

    # 呼叫 OpenAI
    client = _get_client()
    try:
        response = client.responses.create(
            model=model_name,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
        )
    except APITimeoutError:
        raise ConnectionError("OpenAI API 請求超時，請稍後再試。")
    except APIConnectionError:
        raise ConnectionError("無法連線至 OpenAI API，請檢查網路設定。")
    except APIError as e:
        raise RuntimeError(f"OpenAI API 錯誤：{e.message}")

    # 解析回傳
    try:
        raw_text = response.output_text
    except (AttributeError, IndexError):
        raise RuntimeError("OpenAI 回傳格式異常，無法取得回應文字。")

    # 清理 markdown code block
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines)

    try:
        result = json.loads(cleaned)
    except json.JSONDecodeError:
        logger.error("AI 建議 JSON 解析失敗，原始內容: %s", raw_text)
        raise ValueError("AI 回傳格式錯誤，無法解析。請重試。")

    # 基本驗證與預設值
    result.setdefault("overall_status", "注意")
    result.setdefault("status_color", "yellow")
    result.setdefault("summary", "數據分析完成。")
    result.setdefault("alerts", [])
    result.setdefault("recommendations", [])
    result.setdefault("trends", "趨勢分析需要更多數據。")

    logger.info("AI 分析完成：status=%s, alerts=%d, recommendations=%d",
                result["overall_status"], len(result["alerts"]), len(result["recommendations"]))
    return result


def get_sensor_recommendation(sensor_data: dict) -> dict:
    """
    針對單一感測器進行 AI 分析。
    sensor_data 格式同 get_ai_recommendation 中的單筆 dict。
    """
    return get_ai_recommendation([sensor_data])
