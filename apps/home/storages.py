from storages.backends.s3boto3 import S3Boto3Storage

class R2Boto3Storage(S3Boto3Storage):
    """
    自訂 Cloudflare R2 儲存後端，繼承 Django Storages 提供的 S3Boto3Storage。

    Attributes:
        bucket_name (str): R2 儲存桶名稱。
        querystring_auth (bool): 是否在 URL 中簽名授權參數，True 則產生 presigned URL。
        endpoint_url (str): R2 的 S3 相容 API 端點，用於上傳與檔案操作。
        region_name (str | None): AWS 區域名稱，R2 不需要設定，使用 None。
        signature_version (str): 簽名版本，設定為 's3v4'。
        default_acl (str | None): 預設 ACL，R2 不支援傳統 ACL，因此設 None。
        custom_domain (str): 用於給前端生成 URL 的自訂域名，通常為 R2.dev 子域。
    """
    # 儲存桶名稱：請先在環境變數或程式碼中指定
    bucket_name       = 'shanghuyun-platform'

    # 是否在 URL 加上簽名授權參數 (presigned URL)
    querystring_auth  = True

    # S3 API 端點：用於後端檔案讀寫
    endpoint_url      = 'https://4e9bbe760333a36bd94fad22caccc552.r2.cloudflarestorage.com'

    # R2 不需要區域設定
    region_name       = None

    # 使用 v4 簽名
    signature_version = 's3v4'

    # R2 不支援 ACL，保持為 None
    default_acl       = None

    # 前端存取專用域名 (R2.dev 或自訂域)
    custom_domain     = "pub-5049d4dc36de483ab78891fd244767be.r2.dev"