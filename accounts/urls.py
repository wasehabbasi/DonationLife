from django.urls import path
from . import views
from accounts.views import home, eligibility_view

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/donor/', views.donor_dashboard, name='donor_dashboard'),
    path('dashboard/patient/', views.patient_dashboard, name='patient_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('profile/donor/', views.donor_profile, name='donor_profile'),
    path('profile/patient/', views.patient_profile, name='patient_profile'),
    path('profile/admin/', views.admin_profile, name='admin_profile'),
    path('find-donor/', views.find_donor, name='find_donor'),
    path('request-blood/<int:donor_id>/', views.request_blood, name='request_blood'),
    path('admin/request/<int:request_id>/approve', views.approve_request, name='approve_request'),
    path('admin/request/<int:request_id>/reject', views.reject_request, name='reject_request'),
    path('register/', views.register, name='register'),
    path('eligibility/', eligibility_view, name='eligibility'),

    path('admin/donors/', views.admin_all_donors, name='admin_all_donors'),
    path('admin/patients/', views.admin_all_patients, name='admin_all_patients'),
    path('admin/requests/', views.admin_all_requests, name='admin_all_requests'),

    path('donor-requests/', views.donor_received_requests, name='donor_received_requests'),

    path('patient-requests/', views.patient_requests, name='patient_requests'),

    path('chatbot/', views.chatbot_response, name='chatbot_response'),


]
