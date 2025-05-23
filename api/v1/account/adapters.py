from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from .models import User
from allauth.account.models import EmailAddress

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        if sociallogin.is_existing:
            return

        email = sociallogin.account.extra_data.get('email')
        if not email:
            return

        try:
            existing = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return

        # if find account
        request.session['socialaccount_sociallogin'] = sociallogin.serialize()
        raise ImmediateHttpResponse(redirect(reverse('social-choose', args=[existing.pk])))
