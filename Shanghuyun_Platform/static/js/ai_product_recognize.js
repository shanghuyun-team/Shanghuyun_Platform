/**
 * AI 商品圖片辨識 — Wagtail Admin 前端腳本
 * ==========================================
 * 在商品新增/編輯頁面注入「AI 辨識自動填入」按鈕。
 * 點擊後透過 AJAX 呼叫後端 API，自動填入商品名稱、售價、描述。
 *
 * 設計原則：融入 Wagtail admin 原生 UI 風格（teal 主色調、w-panel 結構）
 */
(function () {
    "use strict";

    // ── 設定 ──────────────────────────────────────
    const AI_ENDPOINT = "/admin/product/ai-recognize/";

    // 欄位 ID 對應（Wagtail modeladmin 預設命名）
    const FIELD_MAP = {
        product_name: "id_name",
        suggested_price: "id_price",
        description: "id_description",
    };

    // ── 注入 CSS ─────────────────────────────────
    function injectStyles() {
        if (document.getElementById("ai-recognize-styles")) return;
        const style = document.createElement("style");
        style.id = "ai-recognize-styles";
        style.textContent = `
            /* ─── AI 辨識面板：融入 Wagtail w-panel 風格 ─── */
            .ai-recognize-panel {
                margin: 0 0 2px 0;
                background: var(--w-color-surface-page, #f6f6f8);
                border: 1px solid var(--w-color-border-furniture, #e0e0e0);
                border-radius: 6px;
                overflow: hidden;
                transition: box-shadow 0.2s ease;
            }
            .ai-recognize-panel:hover {
                box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            }

            /* 面板標題列 */
            .ai-recognize-header {
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 14px 20px;
                background: var(--w-color-surface-header, #2e1f5e);
                cursor: default;
            }
            .ai-recognize-header__icon {
                display: flex;
                align-items: center;
                justify-content: center;
                width: 28px;
                height: 28px;
                border-radius: 50%;
                background: rgba(255,255,255,0.15);
                font-size: 15px;
                flex-shrink: 0;
            }
            .ai-recognize-header__title {
                font-size: 14px;
                font-weight: 600;
                color: #fff;
                letter-spacing: 0.3px;
            }
            .ai-recognize-header__badge {
                margin-left: auto;
                padding: 2px 10px;
                border-radius: 12px;
                background: rgba(255,255,255,0.14);
                color: rgba(255,255,255,0.85);
                font-size: 11px;
                font-weight: 500;
                letter-spacing: 0.2px;
            }

            /* 面板內容區 */
            .ai-recognize-body {
                padding: 20px;
            }

            /* 說明文字 */
            .ai-recognize-desc {
                margin: 0 0 16px 0;
                font-size: 13px;
                color: var(--w-color-text-context, #666);
                line-height: 1.6;
            }

            /* 操作列：按鈕 + checkbox */
            .ai-recognize-actions {
                display: flex;
                align-items: center;
                gap: 16px;
                flex-wrap: wrap;
            }

            /* 主按鈕：teal 色系，匹配 Wagtail primary */
            .ai-recognize-btn {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 10px 24px;
                background: var(--w-color-primary, #007d7e);
                color: #fff;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
                box-shadow: 0 1px 3px rgba(0,125,126,0.25);
                line-height: 1.4;
                position: relative;
                overflow: hidden;
            }
            .ai-recognize-btn:hover:not(:disabled) {
                background: var(--w-color-primary-200, #006667);
                box-shadow: 0 3px 8px rgba(0,125,126,0.35);
                transform: translateY(-1px);
            }
            .ai-recognize-btn:active:not(:disabled) {
                transform: translateY(0);
                box-shadow: 0 1px 2px rgba(0,125,126,0.2);
            }
            .ai-recognize-btn:disabled {
                opacity: 0.75;
                cursor: not-allowed;
                transform: none;
            }
            .ai-recognize-btn__icon {
                font-size: 16px;
                line-height: 1;
            }

            /* 載入動畫 */
            .ai-recognize-btn--loading .ai-recognize-btn__icon {
                animation: ai-spin 1.2s linear infinite;
            }
            @keyframes ai-spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            /* 覆蓋模式 checkbox */
            .ai-recognize-overwrite {
                display: flex;
                align-items: center;
                gap: 6px;
                font-size: 13px;
                color: var(--w-color-text-context, #666);
                cursor: pointer;
                user-select: none;
                transition: color 0.15s;
            }
            .ai-recognize-overwrite:hover {
                color: var(--w-color-text-label, #333);
            }
            .ai-recognize-overwrite input[type="checkbox"] {
                width: 16px;
                height: 16px;
                accent-color: var(--w-color-primary, #007d7e);
                cursor: pointer;
            }

            /* 訊息區 */
            .ai-recognize-msg {
                margin-top: 16px;
                padding: 14px 18px;
                border-radius: 5px;
                font-size: 13px;
                line-height: 1.65;
                animation: ai-fade-in 0.3s ease;
            }
            @keyframes ai-fade-in {
                from { opacity: 0; transform: translateY(-4px); }
                to   { opacity: 1; transform: translateY(0); }
            }
            .ai-recognize-msg--success {
                background: #ecfdf5;
                border: 1px solid #a7f3d0;
                color: #065f46;
            }
            .ai-recognize-msg--error {
                background: #fef2f2;
                border: 1px solid #fecaca;
                color: #991b1b;
            }
            .ai-recognize-msg--info {
                background: #f0fdf4;
                border: 1px solid #bbf7d0;
                color: #166534;
            }
            .ai-recognize-msg--warning {
                background: #fffbeb;
                border: 1px solid #fde68a;
                color: #92400e;
            }

            /* 結果摘要 */
            .ai-recognize-msg strong {
                font-weight: 600;
            }
            .ai-recognize-msg .ai-tag {
                display: inline-block;
                padding: 1px 8px;
                border-radius: 10px;
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 0.3px;
                vertical-align: middle;
                margin-left: 4px;
            }
            .ai-tag--high {
                background: #d1fae5;
                color: #065f46;
            }
            .ai-tag--medium {
                background: #fef3c7;
                color: #92400e;
            }
            .ai-tag--low {
                background: #fee2e2;
                color: #991b1b;
            }

            /* 分隔線 */
            .ai-recognize-divider {
                height: 1px;
                background: var(--w-color-border-furniture, #e0e0e0);
                margin: 12px 0;
                border: none;
            }
        `;
        document.head.appendChild(style);
    }

    // ── 工具函式 ──────────────────────────────────
    function getCsrfToken() {
        const input = document.querySelector(
            'input[name="csrfmiddlewaretoken"]'
        );
        if (input) return input.value;
        const match = document.cookie.match(/csrftoken=([^;]+)/);
        return match ? match[1] : "";
    }

    function getImageId() {
        // Wagtail Image chooser widget
        const chooser = document.getElementById("id_image-chooser");
        if (chooser) {
            const hiddenInput = chooser.querySelector(
                'input[type="hidden"]'
            );
            if (hiddenInput && hiddenInput.value) {
                return parseInt(hiddenInput.value, 10) || null;
            }
        }
        const directInput = document.getElementById("id_image");
        if (directInput && directInput.value) {
            return parseInt(directInput.value, 10) || null;
        }
        return null;
    }

    function isProductPage() {
        const path = window.location.pathname;
        return (
            path.includes("/product/create") ||
            path.includes("/product/edit")
        );
    }

    // ── 主邏輯 ────────────────────────────────────
    function init() {
        if (!isProductPage()) return;
        injectStyles();

        const imagePanel = findImagePanel();
        if (!imagePanel) {
            console.warn("[AI辨識] 找不到圖片欄位面板，跳過注入。");
            return;
        }

        const container = createUI();
        imagePanel.parentElement.insertBefore(
            container,
            imagePanel.nextSibling
        );
    }

    function findImagePanel() {
        const labels = document.querySelectorAll("label");
        for (const label of labels) {
            if (
                label.textContent.trim().includes("商品圖片") ||
                label.getAttribute("for") === "id_image"
            ) {
                let el = label.closest(
                    ".w-panel, .object, .field, [data-field]"
                );
                if (el) return el;
                return label.parentElement?.parentElement || label.parentElement;
            }
        }
        const chooser = document.getElementById("id_image-chooser");
        if (chooser) {
            let el = chooser.closest(
                ".w-panel, .object, .field, [data-field]"
            );
            return el || chooser.parentElement;
        }
        return null;
    }

    function createUI() {
        // ── 外層面板 ──
        const panel = document.createElement("div");
        panel.className = "ai-recognize-panel";
        panel.id = "ai-recognize-container";

        // ── 標題列 ──
        const header = document.createElement("div");
        header.className = "ai-recognize-header";

        const icon = document.createElement("span");
        icon.className = "ai-recognize-header__icon";
        icon.textContent = "✨";

        const title = document.createElement("span");
        title.className = "ai-recognize-header__title";
        title.textContent = "AI 智慧辨識";

        const badge = document.createElement("span");
        badge.className = "ai-recognize-header__badge";
        badge.textContent = "自動填入助手";

        header.appendChild(icon);
        header.appendChild(title);
        header.appendChild(badge);

        // ── 內容區 ──
        const body = document.createElement("div");
        body.className = "ai-recognize-body";

        // 說明文字
        const desc = document.createElement("p");
        desc.className = "ai-recognize-desc";
        desc.textContent =
            "選擇商品圖片後，點擊下方按鈕，AI 將分析圖片並自動填入商品名稱、建議售價及商品描述。填入後仍可手動修改。";

        // 操作列
        const actions = document.createElement("div");
        actions.className = "ai-recognize-actions";

        // 主按鈕
        const btn = document.createElement("button");
        btn.type = "button";
        btn.id = "ai-recognize-btn";
        btn.className = "ai-recognize-btn";
        btn.innerHTML =
            '<span class="ai-recognize-btn__icon">✨</span> 分析商品圖片並自動填入';

        // 覆蓋模式
        const overwriteLabel = document.createElement("label");
        overwriteLabel.className = "ai-recognize-overwrite";
        const overwriteCheckbox = document.createElement("input");
        overwriteCheckbox.type = "checkbox";
        overwriteCheckbox.id = "ai-overwrite-mode";
        overwriteLabel.appendChild(overwriteCheckbox);
        overwriteLabel.appendChild(
            document.createTextNode("覆蓋已有內容")
        );

        actions.appendChild(btn);
        actions.appendChild(overwriteLabel);

        // 訊息區
        const msgArea = document.createElement("div");
        msgArea.id = "ai-recognize-msg";
        msgArea.style.display = "none";

        body.appendChild(desc);
        body.appendChild(actions);
        body.appendChild(msgArea);

        panel.appendChild(header);
        panel.appendChild(body);

        // 綁定事件
        btn.addEventListener("click", handleRecognize);

        return panel;
    }

    function showMessage(html, type) {
        const msgArea = document.getElementById("ai-recognize-msg");
        if (!msgArea) return;
        msgArea.style.display = "block";
        msgArea.className = "ai-recognize-msg ai-recognize-msg--" + type;
        msgArea.innerHTML = html;
    }

    function setButtonLoading(loading) {
        const btn = document.getElementById("ai-recognize-btn");
        if (!btn) return;
        if (loading) {
            btn.disabled = true;
            btn.classList.add("ai-recognize-btn--loading");
            btn.innerHTML =
                '<span class="ai-recognize-btn__icon">⚙️</span> AI 辨識中，請稍候…';
        } else {
            btn.disabled = false;
            btn.classList.remove("ai-recognize-btn--loading");
            btn.innerHTML =
                '<span class="ai-recognize-btn__icon">✨</span> 分析商品圖片並自動填入';
        }
    }

    async function handleRecognize() {
        const imageId = getImageId();
        if (!imageId) {
            showMessage(
                "⚠️ 請先在上方選擇商品圖片，再進行 AI 辨識。",
                "warning"
            );
            return;
        }

        setButtonLoading(true);
        showMessage("🔄 正在分析圖片，這可能需要幾秒鐘…", "info");

        try {
            const resp = await fetch(AI_ENDPOINT, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCsrfToken(),
                },
                body: JSON.stringify({ image_id: imageId }),
            });

            const data = await resp.json();

            if (!resp.ok) {
                showMessage(
                    `❌ 辨識失敗：${data.error || "未知錯誤"}`,
                    "error"
                );
                return;
            }

            if (!data.success || !data.data) {
                showMessage("❌ 回傳資料格式異常，請重試。", "error");
                return;
            }

            fillFormFields(data.data);
        } catch (err) {
            console.error("[AI辨識] 請求錯誤:", err);
            showMessage(
                `❌ 網路請求失敗：${err.message || "請檢查網路連線"}`,
                "error"
            );
        } finally {
            setButtonLoading(false);
        }
    }

    function fillFormFields(result) {
        const overwrite = document.getElementById("ai-overwrite-mode");
        const forceOverwrite = overwrite ? overwrite.checked : false;

        let filledFields = [];
        let skippedFields = [];

        // 填入商品名稱
        const nameField = document.getElementById(FIELD_MAP.product_name);
        if (nameField && result.product_name) {
            if (forceOverwrite || !nameField.value.trim()) {
                nameField.value = result.product_name;
                triggerChange(nameField);
                filledFields.push("商品名稱");
            } else {
                skippedFields.push("商品名稱");
            }
        }

        // 填入售價
        const priceField = document.getElementById(FIELD_MAP.suggested_price);
        if (priceField && result.suggested_price !== undefined) {
            if (forceOverwrite || !priceField.value.trim()) {
                priceField.value = result.suggested_price;
                triggerChange(priceField);
                filledFields.push("售價");
            } else {
                skippedFields.push("售價");
            }
        }

        // 填入描述
        const descField = document.getElementById(FIELD_MAP.description);
        if (descField && result.description) {
            if (forceOverwrite || !descField.value.trim()) {
                descField.value = result.description;
                triggerChange(descField);
                filledFields.push("商品描述");
            } else {
                skippedFields.push("商品描述");
            }
        }

        // ── 組裝結果訊息 ──
        const confidence = Math.round((result.confidence || 0) * 100);
        let tagClass, tagLabel;
        if (confidence >= 80) {
            tagClass = "ai-tag--high";
            tagLabel = "高信心";
        } else if (confidence >= 50) {
            tagClass = "ai-tag--medium";
            tagLabel = "中信心";
        } else {
            tagClass = "ai-tag--low";
            tagLabel = "低信心";
        }

        let msg = "";
        if (filledFields.length > 0) {
            msg += `✅ 已填入：<strong>${filledFields.join("、")}</strong>`;
        }
        if (skippedFields.length > 0) {
            if (msg) msg += "<br>";
            msg += `⏭️ 已跳過（欄位已有內容）：${skippedFields.join("、")}`;
        }
        msg += `<hr class="ai-recognize-divider">`;
        msg += `📊 辨識信心度：<strong>${confidence}%</strong> <span class="ai-tag ${tagClass}">${tagLabel}</span>`;

        if (result.needs_review) {
            msg +=
                "<br>⚠️ <strong>建議人工確認</strong> — AI 信心度較低，請仔細檢查上方欄位後再儲存。";
        }

        showMessage(msg, result.needs_review ? "warning" : "success");
    }

    function triggerChange(element) {
        element.dispatchEvent(new Event("input", { bubbles: true }));
        element.dispatchEvent(new Event("change", { bubbles: true }));
    }

    // ── 啟動 ──────────────────────────────────────
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        setTimeout(init, 500);
    }
})();
