from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from django.db import IntegrityError
from datetime import datetime, timedelta
import json

from .models import (
    Doctor, Patient, EmergencyCase, Appointment, 
    Hospital, HomeCareRequest, DoctorActivityLog
)


# ===============================
# HOME / INDEX VIEW
# ===============================
def index(request):
    """Home page with emergency registration form"""
    hospitals = Hospital.objects.filter(is_active=True)[:3]
    context = {
        'hospitals': hospitals,
        'total_cases': EmergencyCase.objects.count(),
        'active_cases': EmergencyCase.objects.filter(status__in=['Waiting', 'Doctor Assigned']).count(),
    }
    return render(request, 'index.html', context)


# ===============================
# PATIENT VIEWS
# ===============================
def patient_login(request):
    """Patient login view"""
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        
        try:
            patient = Patient.objects.get(phone=phone)
            
            # Check password
            if patient.password and check_password(password, patient.password):
                request.session['patient_id'] = patient.id
                request.session['patient_name'] = patient.name
                request.session['patient_phone'] = patient.phone
                messages.success(request, f'Welcome back, {patient.name}!')
                return redirect('patient-dashboard')
            else:
                # If no password set or wrong password
                if not patient.password or patient.password == phone:
                    # First time login with phone as password
                    if password == phone:
                        request.session['patient_id'] = patient.id
                        request.session['patient_name'] = patient.name
                        request.session['patient_phone'] = patient.phone
                        messages.info(request, 'Please change your password for security.')
                        return redirect('patient-dashboard')
                
                messages.error(request, 'Invalid phone number or password')
        except Patient.DoesNotExist:
            messages.error(request, 'No account found with this phone number')
    
    return render(request, 'patient-login.html')


def patient_logout(request):
    """Patient logout"""
    request.session.flush()
    return redirect('home')


def patient_dashboard(request):
    """Patient dashboard showing appointments and cases"""
    patient_id = request.session.get('patient_id')
    
    if not patient_id:
        messages.warning(request, 'Please login to access your dashboard')
        return redirect('patient-login')
    
    patient = get_object_or_404(Patient, id=patient_id)
    
    # Get patient's cases
    emergency_cases = EmergencyCase.objects.filter(
        patient=patient
    ).order_by('-created_at')
    
    # Get patient's appointments
    appointments = Appointment.objects.filter(
        patient=patient
    ).order_by('-appointment_date', '-appointment_time')
    
    # Separate upcoming and past
    today = timezone.now().date()
    upcoming_cases = emergency_cases.filter(
        status__in=['Waiting', 'Doctor Assigned', 'In Progress', 'Doctor En Route']
    )
    past_cases = emergency_cases.filter(
        status__in=['Completed', 'Cancelled']
    )
    
    upcoming_appointments = appointments.filter(
        appointment_date__gte=today,
        status__in=['Scheduled', 'Confirmed']
    )
    past_appointments = appointments.filter(
        status__in=['Completed', 'Cancelled']
    ) | appointments.filter(appointment_date__lt=today)
    
    context = {
        'patient': patient,
        'upcoming_cases': upcoming_cases,
        'past_cases': past_cases,
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
        'total_cases': emergency_cases.count(),
        'total_appointments': appointments.count(),
    }
    return render(request, 'patient-dashboard.html', context)


def patient_change_password(request):
    """Change patient password"""
    patient_id = request.session.get('patient_id')
    
    if not patient_id:
        return redirect('patient-login')
    
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        patient = get_object_or_404(Patient, id=patient_id)
        
        # Verify current password
        if patient.password:
            if not check_password(current_password, patient.password):
                messages.error(request, 'Current password is incorrect')
                return redirect('patient-change-password')
        else:
            # First time password setup
            if current_password != patient.phone:
                messages.error(request, 'Current password should be your phone number')
                return redirect('patient-change-password')
        
        # Check if new passwords match
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match')
            return redirect('patient-change-password')
        
        # Update password
        patient.password = make_password(new_password)
        patient.save()
        
        messages.success(request, 'Password changed successfully!')
        return redirect('patient-dashboard')
    
    return render(request, 'patient-change-password.html')


def patient(request):
    """Render the patient registration page with the full form"""
    # Agar logged in hai toh dashboard bhej do
    if request.session.get('patient_id'):
        return redirect('patient-dashboard')
    
    return render(request, 'patient.html')

# views.py

def patient_register(request):
    """Handle patient registration, session setting and auto-login"""
    if request.method == 'POST':
        name = request.POST.get('pName')
        phone = request.POST.get('pPhone')
        location = request.POST.get('pLocation')
        symptom = request.POST.get('pSymptom')
        care_mode = request.POST.get('careMode', 'hospital')
        
        if name and phone and symptom:
            # 1. Create or get the Patient
            patient, created = Patient.objects.get_or_create(
                phone=phone,
                defaults={
                    'name': name,
                    'patient_id': f'PAT-{timezone.now().strftime("%Y%m%d%H%M%S")}',
                    'location': location or '',
                    'password': make_password(phone)
                }
            )

            # 2. Create Emergency Case LINKED to the patient
            case = EmergencyCase.objects.create(
                patient=patient,  # CRITICAL: This links the case to the patient record
                patient_name=name,
                patient_phone=phone,
                patient_location=location or '',
                symptom=symptom,
                mode='Hospital Emergency' if care_mode == 'hospital' else 'Home Assistance',
                status='Waiting'
            )

            # 3. Set Session for Auto-Login
            request.session['patient_id'] = patient.id
            request.session['patient_name'] = patient.name
            request.session['patient_phone'] = patient.phone
            return redirect('patient-dashboard')
    
    return redirect('index')


# ===============================
# DOCTOR VIEWS
# ===============================
# views.py mein doctor login function
def doctor(request):
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor_id')
        password = request.POST.get('password')
        try:
            doctor = Doctor.objects.get(doctor_id=doctor_id, password=password)
            request.session['doctor_id'] = doctor.id
            request.session['doctor_name'] = doctor.name
            return redirect('doctor-dashboard')
        except Doctor.DoesNotExist:
            messages.error(request, 'Invalid credentials')
    return render(request, 'doctor.html')


def doctor_logout(request):
    """Doctor logout"""
    doctor_id = request.session.get('doctor_id')
    if doctor_id:
        try:
            doctor = Doctor.objects.get(id=doctor_id)
            DoctorActivityLog.objects.create(
                doctor=doctor,
                action='logout',
                description=f'{doctor.name} logged out'
            )
        except Doctor.DoesNotExist:
            pass
    
    request.session.flush()
    messages.success(request, 'Doctor session ended')
    return redirect('home')


def doctor_dashboard(request):
    """Doctor dashboard showing assigned cases"""
    doctor_id = request.session.get('doctor_id')
    
    if not doctor_id:
        return redirect('doctor')
    
    doctor = get_object_or_404(Doctor, id=doctor_id)
    
    # Get assigned cases
    assigned_cases = EmergencyCase.objects.filter(
        assigned_doctor=doctor
    ).order_by('score', 'created_at')
    
    # Get today's appointments
    today = timezone.now().date()
    appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date=today
    ).order_by('appointment_time')
    
    context = {
        'doctor': doctor,
        'cases': assigned_cases,
        'appointments': appointments,
        'total_cases': assigned_cases.count(),
        'pending_cases': assigned_cases.filter(status='Waiting').count(),
    }
    return render(request, 'doctor-dashboard.html', context)


def update_case_status(request, case_id):
    """Update case status from doctor dashboard"""
    if request.method == 'POST':
        case = get_object_or_404(EmergencyCase, id=case_id)
        new_status = request.POST.get('status')
        
        if new_status:
            case.status = new_status
            case.save()
            
            # Log activity
            doctor_id = request.session.get('doctor_id')
            if doctor_id:
                doctor = Doctor.objects.get(id=doctor_id)
                DoctorActivityLog.objects.create(
                    doctor=doctor,
                    action='case_updated',
                    description=f'Updated case {case.token} to {new_status}'
                )
            
            messages.success(request, 'Case status updated')
    
    return redirect('doctor-dashboard')


# ===============================
# APPOINTMENT VIEWS
# ===============================
def appointment(request):
    """Appointment booking page"""
    doctors = Doctor.objects.filter(status__in=['available', 'busy'])
    hospitals = Hospital.objects.filter(is_active=True)
    
    if request.method == 'POST':
        name = request.POST.get('pName')
        phone = request.POST.get('pPhone')
        location = request.POST.get('pLocation')
        doctor_id = request.POST.get('pDoctor')
        hospital_id = request.POST.get('pHospital')
        symptom = request.POST.get('pSymptom')
        date = request.POST.get('appointment_date')
        time = request.POST.get('appointment_time')
        
        if name and phone and doctor_id:
            doctor = get_object_or_404(Doctor, id=doctor_id)
            hospital = None
            if hospital_id:
                hospital = get_object_or_404(Hospital, id=hospital_id)
            
            # 1. Handle User and Patient Creation
            # Create/Get Django User (Required for the Navbar to show 'Logout/Profile')
            user, u_created = User.objects.get_or_create(
                username=phone,
                defaults={
                    'first_name': name,
                    'password': make_password(phone)
                }
            )

            # Create/Get Patient linked to User
            patient, created = Patient.objects.get_or_create(
                phone=phone,
                defaults={
                    'user': user,
                    'name': name,
                    'patient_id': f'PAT-{timezone.now().strftime("%Y%m%d%H%M%S")}',
                    'location': location or '',
                    'password': make_password(phone)
                }
            )
            
            if not created and location:
                patient.location = location
                patient.save()
            
            try:
                # 2. Create the actual appointment
                appointment_obj = Appointment.objects.create(
                    patient=patient,
                    patient_name=name,
                    patient_phone=phone,
                    patient_location=location or '',
                    doctor=doctor,
                    hospital=hospital,
                    appointment_date=date or timezone.now().date(),
                    appointment_time=time or timezone.now().time(),
                    reason=symptom or 'Routine checkup',
                )
                
                # 3. Handle Authentication
                # Log the user in so request.user.is_authenticated becomes True
                login(request, user)
                
                # Update legacy session tracking
                request.session['patient_id'] = patient.id
                request.session['patient_name'] = patient.name
                request.session['patient_phone'] = patient.phone
                
                messages.success(
                    request, 
                    f'Appointment booked with {doctor.name} on {appointment_obj.appointment_date} at {appointment_obj.appointment_time.strftime("%H:%M")}'
                )
                
                # 4. Redirect to Patient Dashboard
                return redirect('patient-dashboard')
                
            except IntegrityError:
                messages.error(
                    request,
                    'This time slot is already booked. Please choose a different time.'
                )
    
    context = {
        'doctors': doctors,
        'hospitals': hospitals,
    }
    return render(request, 'appointment.html', context)


# ===============================
# EMERGENCY QUEUE VIEWS
# ===============================
def emergency_queue(request):
    """Emergency priority queue display"""
    cases = EmergencyCase.objects.filter(
        status__in=['Waiting', 'Doctor Assigned', 'In Progress', 'Doctor En Route']
    ).order_by('score', 'created_at')
    
    context = {
        'cases': cases,
        'total_waiting': cases.filter(status='Waiting').count(),
        'critical_count': cases.filter(priority='Critical').count(),
        'high_count': cases.filter(priority='High').count(),
    }
    return render(request, 'emergency-queue.html', context)


# ===============================
# HOME CARE VIEWS
# ===============================
def home_care(request):
    """Home emergency care request page"""
    if request.method == 'POST':
        name = request.POST.get('hcName')
        issue = request.POST.get('hcIssue')
        mode = request.POST.get('hcMode')
        phone = request.POST.get('hcPhone', '')
        address = request.POST.get('hcAddress', '')
        
        if name and issue and phone:
            # Map mode
            mode_map = {
                'Doctor Home Visit': 'home_visit',
                'Doctor On Call Assistance': 'call_assist'
            }
            
            # Create home care request
            request_obj = HomeCareRequest.objects.create(
                patient_name=name,
                phone=phone,
                address=address,
                issue=issue.lower().replace(' ', '_'),
                mode=mode_map.get(mode, 'home_visit'),
            )
            
            # Also create emergency case
            symptom_map = {
                'Heart Attack Symptoms': 'pain',
                'Breathing Difficulty': 'pain',
                'Stroke Symptoms': 'stroke',
                'Severe Weakness': 'weakness',
            }
            
            # Get or create patient
            patient, created = Patient.objects.get_or_create(
                phone=phone,
                defaults={
                    'name': name,
                    'patient_id': f'PAT-{timezone.now().strftime("%Y%m%d%H%M%S")}',
                    'address': address,
                    'password': make_password(phone)
                }
            )
            
            EmergencyCase.objects.create(
                patient=patient,
                patient_name=name,
                patient_phone=phone,
                patient_location=address,
                symptom=symptom_map.get(issue, 'pain'),
                mode='Doctor Home Visit' if 'Home' in mode else 'Doctor On Call',
                status='Doctor Assigned',
            )
            
            # Store session
            request.session['patient_id'] = patient.id
            request.session['patient_name'] = patient.name
            request.session['patient_phone'] = patient.phone
            
            messages.success(
                request, 
                f'Home care request submitted! Token: {request_obj.token}'
            )
            return redirect('patient-dashboard')
    
    return render(request, 'home-care.html')


def home_tracking(request):
    """Track doctor on the way"""
    patient_id = request.session.get('patient_id')
    
    # Get latest case for this patient
    case = None
    if patient_id:
        case = EmergencyCase.objects.filter(
            patient_id=patient_id,
            mode__in=['Home Assistance', 'Doctor Home Visit']
        ).order_by('-created_at').first()
    
    # Get latest home care request
    home_request = HomeCareRequest.objects.filter().order_by('-created_at').first()
    
    context = {
        'case': case,
        'home_request': home_request,
        'doctor': case.assigned_doctor if case else None,
    }
    return render(request, 'home-tracking.html', context)


# ===============================
# API VIEWS (For AJAX)
# ===============================
def api_emergency_cases(request):
    """API endpoint for getting emergency cases"""
    cases = EmergencyCase.objects.filter(
        status__in=['Waiting', 'Doctor Assigned', 'In Progress']
    ).order_by('score', 'created_at')
    
    data = []
    for idx, case in enumerate(cases, 1):
        data.append({
            'queue_no': idx,
            'token': case.token,
            'name': case.patient_name,
            'symptom': case.get_symptom_display(),
            'priority': case.priority,
            'status': case.status,
            'doctor': case.assigned_doctor.name if case.assigned_doctor else 'Unassigned',
        })
    
    return JsonResponse({'cases': data, 'total': len(data)})


def api_doctor_cases(request):
    """API endpoint for doctor's assigned cases"""
    doctor_id = request.session.get('doctor_id')
    
    if not doctor_id:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    cases = EmergencyCase.objects.filter(
        assigned_doctor_id=doctor_id
    ).order_by('score', 'created_at')
    
    data = []
    for case in cases:
        data.append({
            'id': case.id,
            'token': case.token,
            'name': case.patient_name,
            'symptom': case.get_symptom_display(),
            'mode': case.mode,
            'status': case.status,
            'priority': case.priority,
        })
    
    return JsonResponse({'cases': data})


def api_hospitals(request):
    """API endpoint for hospital network status"""
    hospitals = Hospital.objects.filter(is_active=True)
    
    data = []
    for hospital in hospitals:
        data.append({
            'id': hospital.id,
            'name': hospital.name,
            'load': hospital.get_emergency_load_display(),
            'available_beds': hospital.available_beds,
            'total_beds': hospital.total_beds,
        })
    
    return JsonResponse({'hospitals': data})


# ===============================
# ADMIN DASHBOARD VIEW
# ===============================
@login_required
def admin_dashboard(request):
    """Admin dashboard with statistics"""
    context = {
        'total_doctors': Doctor.objects.count(),
        'total_patients': Patient.objects.count(),
        'total_cases': EmergencyCase.objects.count(),
        'active_cases': EmergencyCase.objects.filter(
            status__in=['Waiting', 'Doctor Assigned']
        ).count(),
        'today_appointments': Appointment.objects.filter(
            appointment_date=timezone.now().date()
        ).count(),
        'recent_cases': EmergencyCase.objects.order_by('-created_at')[:10],
        'doctors': Doctor.objects.all(),
        'hospitals': Hospital.objects.all(),
    }
    return render(request, 'admin/dashboard.html', context)
