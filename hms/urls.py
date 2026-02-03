"""
URL configuration for hms project.
"""

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from hmsapp import views


urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # ===============================
    # HOME & MAIN PAGES
    # ===============================
    path('', views.index, name='index'),
    path('home/', views.index, name='home'),
    
    # ===============================
    # PATIENT URLs
    # ===============================
    path('patient/', views.patient, name='patient'),
    path('patient/login/', views.patient_login, name='patient-login'),
    path('patient/logout/', views.patient_logout, name='patient-logout'),
    path('patient/dashboard/', views.patient_dashboard, name='patient-dashboard'),
    path('patient/change-password/', views.patient_change_password, name='patient-change-password'),
    path('patient/register/', views.patient_register, name='patient-register'),
    
    # ===============================
    # DOCTOR URLs
    # ===============================
    path('doctor/', views.doctor, name='doctor'),
    path('doctor/login/', views.doctor, name='doctor-login'),
    path('doctor/logout/', views.doctor_logout, name='doctor-logout'),
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor-dashboard'),
    path('doctor/case/<int:case_id>/update/', views.update_case_status, name='update-case'),
    
    # ===============================
    # APPOINTMENT URLs
    # ===============================
    path('appointment/', views.appointment, name='appointment'),
    path('appointment/book/', views.appointment, name='appointment-book'),
    
    # ===============================
    # EMERGENCY QUEUE URLs
    # ===============================
    path('emergency-queue/', views.emergency_queue, name='emergency-queue'),
    
    # ===============================
    # HOME CARE URLs
    # ===============================
    path('home-care/', views.home_care, name='home-care'),
    path('home-tracking/', views.home_tracking, name='home-tracking'),
    
    # ===============================
    # API ENDPOINTS (For AJAX/Real-time)
    # ===============================
    path('api/emergency-cases/', views.api_emergency_cases, name='api-emergency-cases'),
    path('api/doctor-cases/', views.api_doctor_cases, name='api-doctor-cases'),
    path('api/hospitals/', views.api_hospitals, name='api-hospitals'),
    
    # ===============================
    # ADMIN DASHBOARD
    # ===============================
    path('admin-dashboard/', views.admin_dashboard, name='admin-dashboard'),
]

# ===============================
# SERVE STATIC & MEDIA FILES (Development Only)
# ===============================
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
