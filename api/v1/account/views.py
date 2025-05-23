from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.models import SocialLogin, EmailAddress
from rest_framework import generics, permissions
from .models import Profile, User
from .serializers import ProfileSerializer
from django.contrib.auth import login as auth_login

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