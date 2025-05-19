from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from .models import User, BloodRequest, Donation  # Adjust as per your models

class CustomAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view))
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        context = dict(
            self.each_context(request),
            donor_count=User.objects.filter(role='donor').count(),
            patient_count=User.objects.filter(role='patient').count(),
            pending_requests=BloodRequest.objects.filter(status='pending').count(),
            recent_donations=Donation.objects.order_by('-created_at')[:5],  # adjust as per your model
        )
        return TemplateResponse(request, "admin/dashboard.html", context)

# Use your custom admin site
custom_admin_site = CustomAdminSite(name='custom_admin')

# Register models to custom admin
custom_admin_site.register(User)
custom_admin_site.register(BloodRequest)
custom_admin_site.register(Donation)
