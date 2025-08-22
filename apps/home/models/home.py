from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel
from django.db import models

from ..blocks import HomePageStreamBlock


class HomePage(Page):
    """網站首頁頁面模型"""
    
    # StreamField 讓管理員可以自由編輯首頁內容
    body = StreamField(
        HomePageStreamBlock(),
        blank=True,
        verbose_name="首頁內容",
        help_text="使用區塊編輯器來建立首頁內容。可以新增、移動和刪除各種內容區塊。"
    )
    
    # 管理面板設定
    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]
    
    # 網頁模板
    template = 'home/home_page.html'
    
    class Meta:
        verbose_name = "首頁"
        verbose_name_plural = "首頁"
