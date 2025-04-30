from rest_framework import serializers
from django.core.files.base import ContentFile
from django_drf_filepond.models import TemporaryUpload
from apps.home.storages import R2Boto3Storage
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    """
    商品序列化器，用於處理商品的新增與圖片上傳。

    Attributes:
        filepond (ListField): 用於接收 FilePond 上傳後返回的暫存 ID 列表，write-only。
        image (ImageField): 讀取用，只讀，代表最終存放在 Cloudflare R2 上的圖片 URL。

    Meta:
        model: 對應的 Model 類別為 Product。
        fields: 指定要輸出的欄位為 id, name, filepond, image。
        read_only_fields: image 欄位只讀。
    """
    filepond = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        help_text="FilePond 暫存上傳 ID 列表"
    )
    image = serializers.ImageField(
        read_only=True,
        help_text="商品圖片的最終 URL，儲存在 Cloudflare R2"
    )

    class Meta:
        model = Product
        fields = ['id', 'name', 'filepond', 'image']
        read_only_fields = ['image']

    def create(self, validated_data):
        """
        新增商品並將 FilePond 暫存檔案上傳至 Cloudflare R2。

        Steps:
        1. 從 validated_data 中取出 filepond 上傳 ID 列表。
        2. 建立 Product 物件，只包含名稱欄位。
        3. 使用自訂的 R2Boto3Storage 來存取 R2。
        4. 逐一讀取每個暫存檔案:
           - 通過 TemporaryUpload 取得暫存檔路徑和檔名。
           - 將檔案內容讀入記憶體 (ContentFile)。
           - 呼叫 storage.save() 上傳到 R2 的 products/ 子目錄。
           - 設定 product.image.name 為上傳後的路徑。
           - 呼叫 tu.delete() 刪除暫存記錄與本機檔案。
        5. 儲存 Product 物件，並回傳。

        Args:
            validated_data (dict): 經過驗證的資料，包含 name 與 filepond 欄位。

        Returns:
            Product: 新增後的 Product 模型實例，image 欄位已更新。
        """
        # 1. 取出 FilePond 上傳的暫存 ID 清單
        upload_ids = validated_data.pop('filepond', [])
        # 2. 先在資料庫建立只有 name 的 Product 物件
        product = Product.objects.create(name=validated_data['name'])
        # 3. 取得 R2 儲存後端實例
        storage = R2Boto3Storage()

        # 4. 處理每個上傳的檔案
        for upload_id in upload_ids:
            # 4.1 取得暫存檔記錄
            tu = TemporaryUpload.objects.get(upload_id=upload_id)
            file_path = tu.file.path  # 本機暫存檔案完整路徑

            # 4.2 讀檔案內容到記憶體
            with open(file_path, 'rb') as f:
                data = f.read()

            # 4.3 封裝成 ContentFile 並上傳到 R2
            cf = ContentFile(data, name=tu.upload_name)
            dest_path = f'products/{tu.upload_name}'
            storage.save(dest_path, cf)

            # 4.4 更新 Product.image 字段
            product.image.name = dest_path

            # 4.5 刪除暫存記錄與本機檔案
            tu.delete()

        # 5. 最後儲存 Product 模型
        product.save()
        return product