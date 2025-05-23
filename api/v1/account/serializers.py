from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['real_name', 'nickname', 'portrait', 'address', 'phone']
    read_only_fields = ()
