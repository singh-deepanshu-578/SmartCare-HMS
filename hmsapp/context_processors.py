"""
Custom context processors for HMS
Add these to TEMPLATES['OPTIONS']['context_processors'] in settings.py
"""

from .models import EmergencyCase, Doctor, Hospital


def hms_stats(request):
    """Add HMS statistics to all templates"""
    return {
        'hms_stats': {
            'total_cases': EmergencyCase.objects.count(),
            'active_cases': EmergencyCase.objects.filter(
                status__in=['Waiting', 'Doctor Assigned']
            ).count(),
            'available_doctors': Doctor.objects.filter(status='available').count(),
            'hospitals_count': Hospital.objects.filter(is_active=True).count(),
        }
    }


def doctor_session(request):
    """Add doctor session info to all templates"""
    return {
        'logged_doctor_id': request.session.get('doctor_id'),
        'logged_doctor_name': request.session.get('doctor_name'),
    }

def user_type_check(request):
    return {
        'hasattr_patient': hasattr(request.user, 'patient') if request.user.is_authenticated else False,
        'hasattr_doctor': hasattr(request.user, 'doctor') if request.user.is_authenticated else False,
    }