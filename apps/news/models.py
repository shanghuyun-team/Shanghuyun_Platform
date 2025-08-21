from django.db import models
from django.urls import reverse
from django.conf import settings
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.search import index
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class NewsCategory(models.Model):
    """消息分類"""
    name = models.CharField(max_length=100, verbose_name='分類名稱')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='網址標識')
    description = models.TextField(blank=True, verbose_name='分類描述')
    color = models.CharField(max_length=7, default='#cda45e', verbose_name='分類顏色')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='建立時間')
    
    class Meta:
        verbose_name = '消息分類'
        verbose_name_plural = '消息分類'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class NewsIndexPage(Page):
    """最新消息首頁"""
    intro = RichTextField(blank=True, verbose_name='頁面介紹')
    
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]
    
    def get_context(self, request):
        context = super().get_context(request)
        # 獲取所有已發布的消息，按建立時間排序
        news_posts = NewsPost.objects.live().order_by('-first_published_at')
        
        # 分頁功能
        from django.core.paginator import Paginator
        paginator = Paginator(news_posts, 6)  # 每頁顯示6則消息
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context['news_posts'] = page_obj
        context['categories'] = NewsCategory.objects.all()
        return context


class NewsPost(Page):
    """消息文章"""
    category = models.ForeignKey(
        NewsCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='分類'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='作者'
    )
    excerpt = models.TextField(max_length=300, verbose_name='摘要')
    featured_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='特色圖片'
    )
    content = StreamField([
        ('heading', blocks.CharBlock(form_classname="title", verbose_name='標題')),
        ('paragraph', blocks.RichTextBlock(verbose_name='段落')),
        ('image', ImageChooserBlock(verbose_name='圖片')),
        ('quote', blocks.BlockQuoteBlock(verbose_name='引用')),
        ('html', blocks.RawHTMLBlock(verbose_name='自訂HTML')),
    ], use_json_field=True, verbose_name='內容')
    
    is_featured = models.BooleanField(default=False, verbose_name='精選文章')
    tags = models.CharField(max_length=200, blank=True, verbose_name='標籤')
    
    search_fields = Page.search_fields + [
        index.SearchField('excerpt'),
        index.SearchField('content'),
        index.SearchField('tags'),
    ]
    
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('category'),
            FieldPanel('author'),
            FieldPanel('is_featured'),
        ], heading='文章設定'),
        FieldPanel('excerpt'),
        FieldPanel('featured_image'),
        FieldPanel('tags'),
        FieldPanel('content'),
    ]
    
    def get_context(self, request):
        context = super().get_context(request)
        # 獲取相關文章
        related_posts = NewsPost.objects.live().exclude(id=self.id)
        if self.category:
            related_posts = related_posts.filter(category=self.category)
        context['related_posts'] = related_posts[:3]
        return context
    
    class Meta:
        verbose_name = '消息文章'
        verbose_name_plural = '消息文章'
