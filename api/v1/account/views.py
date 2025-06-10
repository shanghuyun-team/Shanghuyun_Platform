from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.models import SocialLogin, EmailAddress
from rest_framework import generics, permissions, status
from .models import Profile, User
from .serializers import ProfileSerializer, PasswordChangeSerializer#, AccountDeleteSerializer
from django.contrib.auth import login as auth_login, logout
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

class ProfileRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    """
    GET  /api/profile/ 
    PUT  /api/profile/ 
    PATCH /api/profile/
    """
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile
    
def social_choose(request, pk):
    user = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        choice = request.POST.get('choice')

        data = request.session.pop('socialaccount_sociallogin', None)
        sociallogin = SocialLogin.deserialize(data)

        if choice == 'link':
            sociallogin.connect(request, user)
            
            EmailAddress.objects.update_or_create(
                user=user,
                email=user.email,
                defaults={'verified': True, 'primary': True}
            )
            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        else:
            with transaction.atomic():
                user.delete()
                sociallogin.user.pk = None
                complete_social_login(request, sociallogin)
        
        return redirect('profile')

    return render(request, 'socialaccount/social_choose.html', {
        'existing_user': user,
    })

class PasswordChangeAPIView(generics.UpdateAPIView):
    serializer_class = PasswordChangeSerializer
    model = User
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': '密碼已更新'}, status=status.HTTP_200_OK)
"""
class AccountDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        user = request.user
        serializer = AccountDeleteSerializer(
            data=request.data, 
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # 登出用戶（清除session）
                logout(request)
                
                # 刪除用戶會自動觸發級聯刪除相關的Profile等資料
                # 透過signals.py中的處理器，頭像檔案也會被自動刪除
                user.delete()
                
            return Response(
                {'detail': '帳號已成功刪除'}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'detail': '帳號刪除失敗，請稍後再試'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
"""