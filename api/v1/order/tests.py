import json
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from api.v1.order.views import create_order

User = get_user_model()


class CreateOrderTestCase(TestCase):
    """建立訂單功能測試"""

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword123',
        )

    def test_create_order_requires_post(self):
        """GET 請求應回傳 400"""
        request = self.factory.get('/api/v1/order/create/')
        request.user = self.user
        response = create_order(request)
        self.assertEqual(response.status_code, 400)

    def test_create_order_requires_items(self):
        """空的 items 應回傳 400"""
        payload = {"items": []}
        request = self.factory.post(
            '/api/v1/order/create/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        request.user = self.user
        response = create_order(request)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('error', data)
