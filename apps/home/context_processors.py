from django.templatetags.static import static

def common_static(request):
    return {
        'SALES_STATIC_URL': static('Sales/assets/'),
        'DASHBOARD_STATIC_URL': static('Dashboard/assets/'),
    }
