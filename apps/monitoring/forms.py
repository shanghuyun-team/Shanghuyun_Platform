from django import forms

from .models import Sensor


class SensorForm(forms.ModelForm):
    """感測器新增/編輯表單 — 排除 owner 與 api_key，由後端自動處理"""

    class Meta:
        model = Sensor
        fields = [
            "name",
            "sensor_type",
            "location",
            "description",
            "unit",
            "is_active",
        ]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "例如：溫室一號溫度感測器",
            }),
            "sensor_type": forms.Select(attrs={
                "class": "form-select",
            }),
            "location": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "例如：溫室 A 區",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "備註說明（選填）",
            }),
            "unit": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "例如：°C、%、lux",
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }
