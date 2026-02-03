from django.contrib import admin
from .models import (
    Doctor, Patient, EmergencyCase, Appointment,
    Hospital, HomeCareRequest, DoctorActivityLog
)


# ===============================
# DOCTOR ADMIN
# ===============================
@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['name', 'doctor_id', 'specialization', 'status', 'phone', 'created_at']
    list_filter = ['specialization', 'status', 'created_at']
    search_fields = ['name', 'doctor_id', 'email', 'phone']
    list_editable = ['status']
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'doctor_id', 'specialization')
        }),
        ('Contact Details', {
            'fields': ('phone', 'email')
        }),
        ('Account', {
            'fields': ('user', 'password', 'status'),
            'classes': ('collapse',)
        }),
    )


# ===============================
# PATIENT ADMIN
# ===============================
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['name', 'patient_id', 'phone', 'age', 'gender', 'created_at']
    list_filter = ['gender', 'created_at']
    search_fields = ['name', 'patient_id', 'phone', 'email']
    ordering = ['-created_at']


# ===============================
# EMERGENCY CASE ADMIN
# ===============================
@admin.register(EmergencyCase)
class EmergencyCaseAdmin(admin.ModelAdmin):
    list_display = [
        'token', 'patient_name', 'symptom', 'priority', 
        'assigned_doctor', 'status', 'mode', 'created_at'
    ]
    list_filter = ['priority', 'status', 'symptom', 'mode', 'created_at']
    search_fields = ['token', 'patient_name', 'symptom_description']
    list_editable = ['status']
    ordering = ['score', 'created_at']
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('patient', 'patient_name', 'symptom', 'symptom_description')
        }),
        ('Triage', {
            'fields': ('priority', 'score')
        }),
        ('Assignment', {
            'fields': ('assigned_doctor', 'status', 'mode')
        }),
        ('Tracking', {
            'fields': ('token', 'eta')
        }),
    )
    
    # Color coding by priority
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('patient', 'assigned_doctor')


# ===============================
# APPOINTMENT ADMIN
# ===============================
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        'patient_name', 'doctor', 'appointment_date', 
        'appointment_time', 'status', 'created_at'
    ]
    list_filter = ['status', 'appointment_date', 'created_at']
    search_fields = ['patient_name', 'reason']
    list_editable = ['status']
    ordering = ['appointment_date', 'appointment_time']
    date_hierarchy = 'appointment_date'


# ===============================
# HOSPITAL ADMIN
# ===============================
@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'emergency_load', 'available_beds', 
        'total_beds', 'is_active', 'created_at'
    ]
    list_filter = ['emergency_load', 'is_active', 'created_at']
    search_fields = ['name', 'address']
    list_editable = ['emergency_load', 'is_active']


# ===============================
# HOME CARE REQUEST ADMIN
# ===============================
@admin.register(HomeCareRequest)
class HomeCareRequestAdmin(admin.ModelAdmin):
    list_display = [
        'token', 'patient_name', 'issue', 'mode', 
        'assigned_doctor', 'status', 'created_at'
    ]
    list_filter = ['issue', 'mode', 'status', 'created_at']
    search_fields = ['token', 'patient_name', 'phone', 'address']
    list_editable = ['status']
    ordering = ['-created_at']


# ===============================
# DOCTOR ACTIVITY LOG ADMIN
# ===============================
@admin.register(DoctorActivityLog)
class DoctorActivityLogAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'action', 'description', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['doctor__name', 'description']
    ordering = ['-timestamp']
    readonly_fields = ['doctor', 'action', 'description', 'timestamp']
