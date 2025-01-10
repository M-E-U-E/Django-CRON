# Path: cron_project/cron_project/urls.py

from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from import_export.views import CustomAdminLoginView, DashboardView, home

# Override the default admin login view
admin.site.login = CustomAdminLoginView.as_view()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name="home"),
    path('admin/dashboard/', DashboardView.as_view(), name='admin_dashboard'),
]