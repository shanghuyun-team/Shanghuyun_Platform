from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['real_name', 'nickname', 'portrait', 'address', 'phone']
    read_only_fields = ()

from rest_framework import serializers
from django.conf import settings
from .models import User 

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'is_active',
            'is_staff',
            'is_vendor',
            'date_joined',
        )
        read_only_fields = (
            'email',
            'date_joined',
        )
