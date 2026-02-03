from django.db import models
from django.contrib.auth.models import User
import random
import string

# ===============================
# DOCTOR MODEL
# ===============================
class Doctor(models.Model):
    SPECIALIZATION_CHOICES = [
        ('general', 'General Medicine'),
        ('cardiology', 'Cardiology'),
        ('orthopedics', 'Orthopedics'),
        ('emergency', 'Emergency Medicine'),
        ('pediatrics', 'Pediatrics'),
        ('outpatient', 'Outpatient'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('offline', 'Offline'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    doctor_id = models.CharField(max_length=20, unique=True)
    specialization = models.CharField(max_length=50, choices=SPECIALIZATION_CHOICES, default='general')
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    password = models.CharField(max_length=100, default='doctor123')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.specialization})"
    
    class Meta:
        ordering = ['name']


# ===============================
# PATIENT MODEL (UPDATED)
# ===============================
class Patient(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    patient_id = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=15, unique=True)  # Now unique and required
    email = models.EmailField(blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    address = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)  # NEW: Patient location
    password = models.CharField(max_length=100, default='')  # For patient login
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.patient_id})"
    
    def set_password(self, raw_password):
        """Set password for patient"""
        from django.contrib.auth.hashers import make_password
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        """Check password for patient"""
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password)
    
    class Meta:
        ordering = ['-created_at']


# ===============================
# EMERGENCY CASE MODEL (UPDATED)
# ===============================
class EmergencyCase(models.Model):
    SYMPTOM_CHOICES = [
        ('pain', 'Chest Pain / Breathing Difficulty'),
        ('trauma', 'Severe Physical Injury'),
        ('burn', 'Burns'),
        ('fever', 'High Fever / Flu'),
        ('stroke', 'Stroke Symptoms'),
        ('weakness', 'Severe Weakness'),
        ('routine', 'Routine Checkup'),
    ]
    
    PRIORITY_CHOICES = [
        ('Critical', 'Critical'),
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]
    
    STATUS_CHOICES = [
        ('Waiting', 'Waiting'),
        ('Doctor Assigned', 'Doctor Assigned'),
        ('In Progress', 'In Progress'),
        ('Doctor En Route', 'Doctor En Route'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    
    MODE_CHOICES = [
        ('Hospital Emergency', 'Hospital Emergency'),
        ('Home Assistance', 'Home Assistance'),
        ('Doctor Home Visit', 'Doctor Home Visit'),
        ('Doctor On Call', 'Doctor On Call Assistance'),
    ]
    
    # Patient Information
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True, blank=True)
    patient_name = models.CharField(max_length=100)
    patient_phone = models.CharField(max_length=15, default='')  # NEW
    patient_location = models.CharField(max_length=200, default='')  # NEW
    symptom = models.CharField(max_length=50, choices=SYMPTOM_CHOICES)
    symptom_description = models.TextField(blank=True)
    
    # Triage Information
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Low')
    score = models.PositiveIntegerField(default=3)
    
    # Assignment
    assigned_doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_hospital = models.ForeignKey('Hospital', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Status & Mode
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Waiting')
    mode = models.CharField(max_length=30, choices=MODE_CHOICES, default='Hospital Emergency')
    
    # Token & Tracking
    token = models.CharField(max_length=20, unique=True)
    eta = models.CharField(max_length=50, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Auto-generate token if not set
        if not self.token:
            prefix = 'HC-' if 'Home' in self.mode or 'Call' in self.mode else 'SC-'
            self.token = prefix + ''.join(random.choices(string.digits, k=4))
        
        # Auto-assign priority based on symptom
        symptom_priority = {
            'pain': ('Critical', 1),
            'trauma': ('High', 2),
            'burn': ('High', 2),
            'stroke': ('Critical', 1),
            'weakness': ('Medium', 3),
            'fever': ('Medium', 3),
            'routine': ('Low', 4),
        }
        
        if not self.pk:  # Only on creation
            self.priority, self.score = symptom_priority.get(self.symptom, ('Low', 4))
            
            # Auto-assign doctor based on symptom
            if not self.assigned_doctor:
                self.assigned_doctor = self.get_best_doctor()
            
            # Auto-assign hospital
            if not self.assigned_hospital:
                self.assigned_hospital = self.get_best_hospital()
        
        super().save(*args, **kwargs)
    
    def get_best_doctor(self):
        """Get the best available doctor based on symptom"""
        symptom_doctor_map = {
            'pain': ['emergency', 'cardiology'],
            'trauma': ['emergency', 'orthopedics'],
            'burn': ['emergency'],
            'stroke': ['emergency', 'cardiology'],
            'weakness': ['general'],
            'fever': ['general', 'outpatient'],
            'routine': ['general', 'outpatient'],
        }
        
        specializations = symptom_doctor_map.get(self.symptom, ['general'])
        
        for spec in specializations:
            doctor = Doctor.objects.filter(
                specialization=spec,
                status='available'
            ).first()
            if doctor:
                return doctor
        
        return Doctor.objects.filter(status='available').first()
    
    def get_best_hospital(self):
        """Get the best available hospital"""
        from django.db.models import Q
        
        # Prefer hospitals with low load
        hospital = Hospital.objects.filter(
            is_active=True,
            emergency_load__in=['low', 'medium']
        ).order_by('emergency_load').first()
        
        if not hospital:
            hospital = Hospital.objects.filter(is_active=True).first()
        
        return hospital
    
    def __str__(self):
        return f"{self.token} - {self.patient_name} ({self.priority})"
    
    class Meta:
        ordering = ['score', 'created_at']


# ===============================
# APPOINTMENT MODEL (UPDATED)
# ===============================
class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('Confirmed', 'Confirmed'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True, blank=True)
    patient_name = models.CharField(max_length=100)
    patient_phone = models.CharField(max_length=15, default='')  # NEW
    patient_location = models.CharField(max_length=200, default='')  # NEW
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    hospital = models.ForeignKey('Hospital', on_delete=models.SET_NULL, null=True, blank=True)
    
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason = models.TextField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled')
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.patient_name} - {self.doctor.name} ({self.appointment_date})"
    
    class Meta:
        ordering = ['appointment_date', 'appointment_time']
        unique_together = ['doctor', 'appointment_date', 'appointment_time']  # Prevent double booking


# ===============================
# HOSPITAL MODEL
# ===============================
class Hospital(models.Model):
    LOAD_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('very_high', 'Very High'),
    ]
    
    name = models.CharField(max_length=200)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    
    emergency_load = models.CharField(max_length=20, choices=LOAD_CHOICES, default='low')
    is_active = models.BooleanField(default=True)
    
    total_beds = models.PositiveIntegerField(default=100)
    available_beds = models.PositiveIntegerField(default=50)
    
    image = models.ImageField(upload_to='hospitals/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


# ===============================
# HOME CARE REQUEST MODEL
# ===============================
class HomeCareRequest(models.Model):
    ISSUE_CHOICES = [
        ('heart_attack', 'Heart Attack Symptoms'),
        ('breathing', 'Breathing Difficulty'),
        ('stroke', 'Stroke Symptoms'),
        ('weakness', 'Severe Weakness'),
    ]
    
    MODE_CHOICES = [
        ('home_visit', 'Doctor Home Visit'),
        ('call_assist', 'Doctor On Call Assistance'),
    ]
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Doctor En Route', 'Doctor En Route'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    
    patient_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    issue = models.CharField(max_length=50, choices=ISSUE_CHOICES)
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='home_visit')
    
    assigned_doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    eta = models.CharField(max_length=50, default='15-20 mins')
    token = models.CharField(max_length=20, unique=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = 'HC-' + ''.join(random.choices(string.digits, k=4))
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.token} - {self.patient_name}"
    
    class Meta:
        ordering = ['-created_at']


# ===============================
# DOCTOR ACTIVITY LOG MODEL
# ===============================
class DoctorActivityLog(models.Model):
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('case_assigned', 'Case Assigned'),
        ('case_updated', 'Case Updated'),
        ('case_completed', 'Case Completed'),
    ]
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.doctor.name} - {self.action}"
    
    class Meta:
        ordering = ['-timestamp']
