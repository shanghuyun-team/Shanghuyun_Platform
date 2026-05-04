/**
 * AI 商品圖片辨識 — Wagtail Admin 前端腳本
 * ==========================================
 * 在商品新增/編輯頁面注入「AI 辨識自動填入」按鈕。
 * 點擊後透過 AJAX 呼叫後端 API，自動填入商品名稱、售價、描述。
 *
 * 設計原則：融入 Wagtail admin 原生 UI 風格（teal 主色調、w-panel 結構）
 * 樣式由獨立 CSS 檔案管理（ai_product_recognize.css）
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

        // 初始化步驟狀態
        updateSteps(getImageId() ? 1 : 0);
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

        // ── 步驟指示器 ──
        const steps = createSteps();

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

        // 進度條
        const progress = createProgressBar();

        // 訊息區
        const msgArea = document.createElement("div");
        msgArea.id = "ai-recognize-msg";
        msgArea.style.display = "none";

        body.appendChild(steps);
        body.appendChild(actions);
        body.appendChild(progress);
        body.appendChild(msgArea);

        panel.appendChild(header);
        panel.appendChild(body);

        // 綁定事件
        btn.addEventListener("click", handleRecognize);

        // 監聽圖片選擇器變化
        observeImageChooser();

        return panel;
    }

    function createSteps() {
        const container = document.createElement("div");
        container.className = "ai-recognize-steps";
        container.id = "ai-recognize-steps";

        const stepsData = [
            { num: "1", label: "選擇圖片" },
            { num: "2", label: "AI 分析" },
            { num: "3", label: "自動填入" },
        ];

        stepsData.forEach((s, i) => {
            const step = document.createElement("div");
            step.className = "ai-step";
            step.id = `ai-step-${i}`;

            const num = document.createElement("span");
            num.className = "ai-step__number";
            num.textContent = s.num;

            const label = document.createElement("span");
            label.className = "ai-step__label";
            label.textContent = s.label;

            step.appendChild(num);
            step.appendChild(label);
            container.appendChild(step);

            if (i < stepsData.length - 1) {
                const connector = document.createElement("div");
                connector.className = "ai-step-connector";
                connector.id = `ai-connector-${i}`;
                container.appendChild(connector);
            }
        });

        return container;
    }

    function createProgressBar() {
        const wrapper = document.createElement("div");
        wrapper.className = "ai-recognize-progress";
        wrapper.id = "ai-recognize-progress";

        const bar = document.createElement("div");
        bar.className = "ai-progress-bar";

        const fill = document.createElement("div");
        fill.className = "ai-progress-fill";
        fill.id = "ai-progress-fill";

        const text = document.createElement("div");
        text.className = "ai-progress-text";
        text.id = "ai-progress-text";
        text.textContent = "準備中...";

        bar.appendChild(fill);
        wrapper.appendChild(bar);
        wrapper.appendChild(text);

        return wrapper;
    }

    function updateSteps(activeIndex) {
        for (let i = 0; i < 3; i++) {
            const step = document.getElementById(`ai-step-${i}`);
            const connector = document.getElementById(`ai-connector-${i}`);
            if (!step) continue;

            step.classList.remove("ai-step--active", "ai-step--done");
            if (connector) connector.classList.remove("ai-step-connector--done");

            if (i < activeIndex) {
                step.classList.add("ai-step--done");
                if (connector) connector.classList.add("ai-step-connector--done");
            } else if (i === activeIndex) {
                step.classList.add("ai-step--active");
            }
        }
    }

    function showProgress(visible) {
        const el = document.getElementById("ai-recognize-progress");
        if (el) {
            if (visible) {
                el.classList.add("ai-recognize-progress--visible");
            } else {
                el.classList.remove("ai-recognize-progress--visible");
            }
        }
    }

    function updateProgress(percent, text) {
        const fill = document.getElementById("ai-progress-fill");
        const txt = document.getElementById("ai-progress-text");
        if (fill) fill.style.width = percent + "%";
        if (txt) txt.textContent = text;
    }

    function observeImageChooser() {
        // 監聽圖片選擇器的 DOM 變化來更新步驟狀態
        const chooser = document.getElementById("id_image-chooser");
        if (!chooser) return;

        const observer = new MutationObserver(() => {
            const hasImage = !!getImageId();
            updateSteps(hasImage ? 1 : 0);
        });
        observer.observe(chooser, { childList: true, subtree: true, attributes: true });
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
        updateSteps(1);
        showProgress(true);
        updateProgress(15, "🔍 正在上傳圖片…");

        // 隱藏之前的訊息
        const msgArea = document.getElementById("ai-recognize-msg");
        if (msgArea) msgArea.style.display = "none";

        // 模擬進度
        const progressTimer = setInterval(() => {
            const fill = document.getElementById("ai-progress-fill");
            if (fill) {
                const current = parseFloat(fill.style.width) || 15;
                if (current < 85) {
                    const next = current + (85 - current) * 0.08;
                    updateProgress(
                        Math.min(next, 85),
                        current < 40 ? "🤖 AI 正在分析圖片…" : "📝 正在生成商品資訊…"
                    );
                }
            }
        }, 300);

        try {
            updateSteps(1);

            const resp = await fetch(AI_ENDPOINT, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCsrfToken(),
                },
                body: JSON.stringify({ image_id: imageId }),
            });

            clearInterval(progressTimer);
            updateProgress(95, "✅ 分析完成，正在填入…");

            const data = await resp.json();

            if (!resp.ok) {
                updateProgress(100, "❌ 辨識失敗");
                updateSteps(1);
                showMessage(
                    `❌ 辨識失敗：${data.error || "未知錯誤"}`,
                    "error"
                );
                setTimeout(() => showProgress(false), 1500);
                return;
            }

            if (!data.success || !data.data) {
                updateProgress(100, "❌ 回傳異常");
                updateSteps(1);
                showMessage("❌ 回傳資料格式異常，請重試。", "error");
                setTimeout(() => showProgress(false), 1500);
                return;
            }

            updateSteps(2);
            updateProgress(100, "✅ 完成！");

            // 稍微延遲填入，讓使用者看到進度完成
            await new Promise(r => setTimeout(r, 300));
            fillFormFields(data.data);
            updateSteps(2); // All done

            setTimeout(() => showProgress(false), 2000);
        } catch (err) {
            clearInterval(progressTimer);
            console.error("[AI辨識] 請求錯誤:", err);
            updateProgress(100, "❌ 網路錯誤");
            updateSteps(1);
            showMessage(
                `❌ 網路請求失敗：${err.message || "請檢查網路連線"}`,
                "error"
            );
            setTimeout(() => showProgress(false), 1500);
        } finally {
            setButtonLoading(false);
        }
    }

    function highlightField(field) {
        if (!field) return;
        field.classList.remove("ai-field-highlighted");
        // Force reflow to restart animation
        void field.offsetWidth;
        field.classList.add("ai-field-highlighted");
        setTimeout(() => {
            field.classList.remove("ai-field-highlighted");
        }, 1500);
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
                highlightField(nameField);
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
                highlightField(priceField);
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
                highlightField(descField);
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

        // 結果卡片
        msg += `<div class="ai-result-cards">`;
        msg += `<div class="ai-result-card">
                    <div class="ai-result-card__label">商品名稱</div>
                    <div class="ai-result-card__value">${result.product_name || '—'}</div>
                </div>`;
        msg += `<div class="ai-result-card">
                    <div class="ai-result-card__label">建議售價</div>
                    <div class="ai-result-card__value">NT$ ${result.suggested_price || '—'}</div>
                </div>`;
        msg += `<div class="ai-result-card">
                    <div class="ai-result-card__label">辨識信心度</div>
                    <div class="ai-result-card__value">${confidence}% <span class="ai-tag ${tagClass}">${tagLabel}</span></div>
                </div>`;
        msg += `</div>`;

        if (result.needs_review) {
            msg +=
                '<br>⚠️ <strong>建議人工確認</strong> — AI 信心度較低，請仔細檢查上方欄位後再儲存。';
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
