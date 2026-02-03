from django import forms
from .models import (
    Doctor, Patient, EmergencyCase, Appointment,
    Hospital, HomeCareRequest
)


# ===============================
# EMERGENCY CASE FORM
# ===============================
class EmergencyCaseForm(forms.ModelForm):
    class Meta:
        model = EmergencyCase
        fields = ['patient_name', 'symptom', 'symptom_description', 'mode']
        widgets = {
            'patient_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter patient name',
                'required': True
            }),
            'symptom': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'symptom_description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe symptoms in detail',
                'rows': 3
            }),
            'mode': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
        }



# ===============================
# APPOINTMENT FORM
# ===============================
class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient_name', 'doctor', 'appointment_date', 'appointment_time', 'reason']
        widgets = {
            'patient_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your name'
            }),
            'doctor': forms.Select(attrs={
                'class': 'form-select'
            }),
            'appointment_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'appointment_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Reason for visit',
                'rows': 3
            }),
        }


# ===============================
# HOME CARE REQUEST FORM
# ===============================
class HomeCareRequestForm(forms.ModelForm):
    class Meta:
        model = HomeCareRequest
        fields = ['patient_name', 'phone', 'address', 'issue', 'mode']
        widgets = {
            'patient_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Patient Name',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contact Number',
                'required': True
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Full Address',
                'rows': 3,
                'required': True
            }),
            'issue': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'mode': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
        }


# ===============================
# DOCTOR LOGIN FORM
# ===============================
# forms.py

class DoctorLoginForm(forms.Form):
    doctor_id = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Doctor ID (e.g. DOC001)',
            'required': True
        }),
        label='Doctor ID'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Password',
            'required': True
        }),
        label='Password'
    )


# ===============================
# PATIENT REGISTRATION FORM
# ===============================
class PatientRegistrationForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'phone', 'email', 'age', 'gender', 'address']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full Name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address'
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Age'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-select'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Address',
                'rows': 2
            }),
        }
