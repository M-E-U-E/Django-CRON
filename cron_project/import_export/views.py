from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

class CustomAdminLoginView(LoginView):
    template_name = 'admin/custom_login.html'
    success_url = reverse_lazy('admin:index')
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return self.success_url

    def form_invalid(self, form):
        """Add custom error handling here if needed"""
        return super().form_invalid(form)