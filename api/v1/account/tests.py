from django.test import TestCase
from rest_framework.test import APIClient
from .models import User

class UserAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(username='admin', password='pass123')
        self.client.force_authenticate(user=self.admin)

    def test_list_users(self):
        response = self.client.get('/api/v1/account/users/')
        self.assertEqual(response.status_code, 200)
