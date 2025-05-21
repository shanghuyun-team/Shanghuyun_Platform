# apps/users/views.py
from django.views.generic import TemplateView

class RegisterPageView(TemplateView):
    template_name = 'users/register_page.html'

class LoginPageView(TemplateView):
    template_name = 'users/login_page.html'

class ProfilePageView(TemplateView):
    template_name = 'users/profile_page.html'