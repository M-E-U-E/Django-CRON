from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.db.models import Sum, Count
from django.shortcuts import render
from .models import KayakTransaction  # Add this import
from django.db.models.functions import TruncMonth
import plotly.graph_objects as go
import pandas as pd

def home(request):
    return render(request, 'admin/custom_login.html')

class CustomAdminLoginView(LoginView):
    template_name = 'admin/custom_login.html'
    success_url = reverse_lazy('admin:index')
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return self.success_url

    def form_invalid(self, form):
        """Add custom error handling here if needed"""
        return super().form_invalid(form)
    

@method_decorator(staff_member_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'admin/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get transactions data
        transactions = KayakTransaction.objects.all()
        
        # Monthly revenue
        monthly_revenue = (
            transactions
            .annotate(month=TruncMonth('lead_date'))
            .values('month')
            .annotate(
                total_revenue=Sum('revenue'),
                total_commission=Sum('commission')
            )
            .order_by('month')
        )
        
        # Create revenue graph
        df = pd.DataFrame(monthly_revenue)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['month'],
            y=df['total_revenue'],
            name='Revenue',
            line=dict(color='#4F46E5')
        ))
        fig.add_trace(go.Scatter(
            x=df['month'],
            y=df['total_commission'],
            name='Commission',
            line=dict(color='#EC4899')
        ))
        
        context['revenue_chart'] = fig.to_html(
            full_html=False,
            config={'displayModeBar': False}
        )
        
        # Add summary statistics
        context['total_transactions'] = transactions.count()
        context['total_revenue'] = transactions.aggregate(Sum('revenue'))['revenue__sum']
        context['avg_commission'] = transactions.aggregate(Sum('commission'))['commission__sum']
        
        return context