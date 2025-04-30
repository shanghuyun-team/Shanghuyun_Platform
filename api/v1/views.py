# apps/sale/views.py
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    """
    ProductViewSet

    提供完整的 CRUD 接口，用於管理 Product 模型，
    包含取得商品列表、檢視單一商品、新增、更新與刪除。

    Attributes:
        queryset (QuerySet): 預設查詢集，返回所有 Product 物件。
        serializer_class (Serializer): 指定使用的序列化器為 ProductSerializer。
        parser_classes (list): 解析請求內容的解析器列表，支援 Multipart/form-data 和表單。
    """
    # 查詢所有 Product
    queryset = Product.objects.all()
    # 指定序列化類別
    serializer_class = ProductSerializer
    # 處理 multipart/form-data 和普通表單，支援 FilePond 送出的檔案上傳
    parser_classes = [
        MultiPartParser,  # 解析 file upload
        FormParser        # 解析表單欄位
    ]
