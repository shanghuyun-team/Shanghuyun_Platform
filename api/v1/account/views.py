from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Profile, User
from allauth.account.models import EmailAddress
from .serializers import ProfileSerializer, UserSerializer

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
    
class UserRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    """
    GET  /api/user/ 
    PUT  /api/user/ 
    PATCH /api/user/
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
    
class EmailVerifiedAPIView(APIView):
    """
    GET /api/user/<int:pk>/email-verified/
    回傳指定 user.pk 的信箱是否已驗證。
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if not (request.user.is_staff or request.user.pk == user.pk):
            return Response(
                {"detail": "Permission denied."},
                status=status.HTTP_403_FORBIDDEN
            )

        verified = EmailAddress.objects.filter(
            user=user,
            email=user.email,
            verified=True
        ).exists()

        return Response({"email_verified": verified})