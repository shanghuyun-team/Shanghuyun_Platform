import logging

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.core.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from allauth.account.utils import perform_login
from .models import User
from allauth.account.models import EmailAddress
from django.conf import settings

logger = logging.getLogger(__name__)


def _get_site_name():
    """從 SiteBasicSetting 取得網站名稱，失敗時回傳 None。"""
    try:
        from apps.home.models.site_settings import SiteBasicSetting
        setting = SiteBasicSetting.objects.first()
        if setting and setting.site_name:
            return setting.site_name
    except Exception:
        logger.debug("SiteBasicSetting 尚未建立或無法讀取，使用預設 site name")
    return None


class MyAccountAdapter(DefaultAccountAdapter):
    """
    自訂帳號 Adapter：將 allauth 寄信時使用的 current_site.name
    替換為 SiteBasicSetting 中設定的 site_name，
    避免信件出現預設的 "example.com"。
    """

    def _patch_site_name(self, site):
        """如果 SiteBasicSetting 有設定 site_name，覆寫 site 物件的 name。"""
        site_name = _get_site_name()
        if site_name:
            site.name = site_name
        return site

    def send_mail(self, template_prefix, email, context):
        from allauth.core import context as allauth_context
        from django.contrib.sites.shortcuts import get_current_site

        request = allauth_context.request
        site = get_current_site(request)
        self._patch_site_name(site)

        ctx = {
            "request": request,
            "email": email,
            "current_site": site,
        }
        ctx.update(context)
        msg = self.render_mail(template_prefix, email, ctx)
        msg.send()

    def format_email_subject(self, subject):
        from allauth.account import app_settings
        from django.utils.encoding import force_str

        prefix = app_settings.EMAIL_SUBJECT_PREFIX
        if prefix is None:
            site_name = _get_site_name()
            if not site_name:
                from allauth.core import context as allauth_context
                from django.contrib.sites.shortcuts import get_current_site
                site_name = get_current_site(allauth_context.request).name
            prefix = "[{name}] ".format(name=site_name)
        return prefix + force_str(subject)


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

        sociallogin.connect(request, existing)
        perform_login(request, existing, email_verification='optional')
        raise ImmediateHttpResponse(redirect(settings.LOGIN_REDIRECT_URL))
