"""
Management command to populate HMS with sample data
Usage: python manage.py populate_data
"""

from django.core.management.base import BaseCommand
from django.core.files import File
from hmsapp.models import Doctor, Hospital, Patient
import os


class Command(BaseCommand):
    help = 'Populate the database with sample data for HMS'

    def handle(self, *args, **kwargs):
        self.stdout.write('Populating database with sample data...')
        
        # Create Doctors
        doctors_data = [
            {
                'name': 'Dr. Sharma',
                'doctor_id': 'DOC001',
                'specialization': 'emergency',
                'phone': '9876543210',
                'email': 'sharma@hms.com',
                'password': 'sharma123',
                'status': 'available'
            },
            {
                'name': 'Dr. Mehta',
                'doctor_id': 'DOC002',
                'specialization': 'general',
                'phone': '9876543211',
                'email': 'mehta@hms.com',
                'password': 'mehta123',
                'status': 'available'
            },
            {
                'name': 'Dr. Verma',
                'doctor_id': 'DOC003',
                'specialization': 'outpatient',
                'phone': '9876543212',
                'email': 'verma@hms.com',
                'password': 'verma123',
                'status': 'available'
            },
            {
                'name': 'Dr. Patel',
                'doctor_id': 'DOC004',
                'specialization': 'cardiology',
                'phone': '9876543213',
                'email': 'patel@hms.com',
                'password': 'patel123',
                'status': 'busy'
            },
            {
                'name': 'Dr. Gupta',
                'doctor_id': 'DOC005',
                'specialization': 'orthopedics',
                'phone': '9876543214',
                'email': 'gupta@hms.com',
                'password': 'gupta123',
                'status': 'available'
            },
        ]
        
        for doc_data in doctors_data:
            doctor, created = Doctor.objects.get_or_create(
                doctor_id=doc_data['doctor_id'],
                defaults=doc_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created doctor: {doctor.name}'))
            else:
                self.stdout.write(f'Doctor already exists: {doctor.name}')
        
        # Create Hospitals
        hospitals_data = [
            {
                'name': 'AIIMS Delhi',
                'address': 'Sri Aurobindo Marg, Ansari Nagar, New Delhi - 110029',
                'phone': '011-26588500',
                'emergency_load': 'very_high',
                'total_beds': 2000,
                'available_beds': 150,
                'is_active': True,
                'image_name': 'aiimsdelhi.jpg'
            },
            {
                'name': 'Safdarjung Hospital, Delhi',
                'address': 'Ansari Nagar West, New Delhi - 110029',
                'phone': '011-26165060',
                'emergency_load': 'high',
                'total_beds': 1500,
                'available_beds': 300,
                'is_active': True,
                'image_name': 'safhospi.jpg'
            },
            {
                'name': 'Max Super Speciality Hospital, Delhi',
                'address': 'Press Enclave Road, Saket, New Delhi - 110017',
                'phone': '011-26515050',
                'emergency_load': 'low',
                'total_beds': 500,
                'available_beds': 200,
                'is_active': True,
                'image_name': 'maxhospital.jpg'
            },
        ]
        
        for hosp_data in hospitals_data:
            image_name = hosp_data.pop('image_name', None)
            hospital, created = Hospital.objects.get_or_create(
                name=hosp_data['name'],
                defaults=hosp_data
            )
            
            # Try to add image if available
            if created and image_name:
                # Try to find image in static/images
                image_path = os.path.join('static', 'images', image_name)
                if os.path.exists(image_path):
                    try:
                        with open(image_path, 'rb') as img_file:
                            hospital.image.save(image_name, File(img_file), save=True)
                        self.stdout.write(f'  Added image for {hospital.name}')
                    except Exception as e:
                        self.stdout.write(f'  Could not add image: {str(e)}')
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created hospital: {hospital.name}'))
            else:
                self.stdout.write(f'Hospital already exists: {hospital.name}')
        
        self.stdout.write(self.style.SUCCESS('\nDatabase populated successfully!'))
        self.stdout.write('')
        self.stdout.write('=' * 60)
        self.stdout.write('DEMO LOGIN CREDENTIALS')
        self.stdout.write('=' * 60)
        self.stdout.write('')
        self.stdout.write('DOCTOR LOGIN:')
        self.stdout.write('  Dr. Sharma (Emergency): DOC001 / sharma123')
        self.stdout.write('  Dr. Mehta (General): DOC002 / mehta123')
        self.stdout.write('  Dr. Verma (Outpatient): DOC003 / verma123')
        self.stdout.write('  Dr. Patel (Cardiology): DOC004 / patel123')
        self.stdout.write('  Dr. Gupta (Orthopedics): DOC005 / gupta123')
        self.stdout.write('')
        self.stdout.write('PATIENT LOGIN:')
        self.stdout.write('  Register first with your mobile number')
        self.stdout.write('  Default password = your mobile number')
        self.stdout.write('  Login at: /patient/login/')
        self.stdout.write('')
        self.stdout.write('=' * 60)
