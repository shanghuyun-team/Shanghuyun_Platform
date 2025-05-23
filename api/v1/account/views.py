from rest_framework import generics, permissions
from .models import Profile
from rest_framework import generics, permissions
from .models import Profile
from .serializers import ProfileSerializer

class ProfileRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    """
    GET  /api/profile/    -> return user.profile
    PUT  /api/profile/    -> update all
    PATCH /api/profile/   -> update partial
    """
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile
