from wagtail_modeladmin.options import ModelAdmin, modeladmin_register
from .models import User#, Profile

class UserAdmin(ModelAdmin):
    model = User
    menu_label = '用戶管理'
    menu_icon = 'user'
    list_display = ('username', 'is_active', 'is_staff', 'is_vendor')
    search_fields = ('username',)
modeladmin_register(UserAdmin)

"""
class ProfileAdmin(ModelAdmin):
    model = Profile
    menu_label = '個人檔案'
    menu_icon = 'form'
    list_display = ('user', 'email', 'real_name', 'nickname')
    search_fields = ('user__username', 'email', 'real_name')

modeladmin_register(ProfileAdmin)
"""