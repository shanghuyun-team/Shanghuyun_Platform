# apps/users/views.py
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

class ProfilePageView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile_page.html'
    login_url = reverse_lazy('account_login')  # 未登入時導向的 URL，這裡使用 allauth 的登入 URL

class PrivacyPolicyPageView(TemplateView):
    template_name = 'users/privacy_policy.html'

class TermsOfServicePageView(TemplateView):
    template_name = 'users/terms_of_service.html'