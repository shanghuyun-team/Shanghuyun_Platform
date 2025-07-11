# apps/users/views.py
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import render
from apps.users.models.privacy_policy import SitePolicySetting
from apps.users.models.terms_of_service import SiteTermsSetting

class ProfilePageView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile_page.html'
    login_url = reverse_lazy('account_login')  # 未登入時導向的 URL，這裡使用 allauth 的登入 URL

def privacy_policy(request):
    # load() 会根据当前站点（或所有站点）拿到唯一的那条设置
    site_policy = SitePolicySetting.load(request_or_site=request)
    return render(request, "users/privacy_policy.html", {
        "site_policy": site_policy,
    })

def terms_of_service(request):
    # load() 会根据当前站点（或所有站点）拿到唯一的那条设置
    site_terms = SiteTermsSetting.load(request_or_site=request)
    return render(request, "users/terms_of_service_page.html", {
        "site_terms": site_terms,
    })