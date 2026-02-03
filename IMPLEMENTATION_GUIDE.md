# HMS Django Project - Implementation Guide for Updates

## Overview of Changes

This guide covers the implementation of the following new features:
1. Patient Login System with mobile number
2. Patient Dashboard with appointments and cases
3. Password Change functionality
4. Mobile number and location fields in emergency and appointment forms
5. Prevention of double-booking for appointments
6. Auto-redirect to patient dashboard after booking

## Files Modified/Created

### 1. Models (models.py)
**Changes:**
- Added `user` field to Patient model for authentication
- Added `phone` field as unique identifier
- Added `location` field for patient address
- Added `password` field with hashing methods
- Added `patient_phone` and `patient_location` to EmergencyCase
- Added `patient_phone` and `patient_location` to Appointment
- Added `unique_together` constraint to Appointment for preventing double-booking
- Added `assigned_hospital` field to EmergencyCase

### 2. Views (views.py)
**New Views Created:**
- `patient_login()` - Handle patient login
- `patient_logout()` - Handle patient logout
- `patient_dashboard()` - Display patient dashboard
- `patient_change_password()` - Change password functionality

**Modified Views:**
- `patient_register()` - Now creates patient account and redirects to dashboard
- `appointment()` - Added phone, location fields and double-booking prevention
- `home_care()` - Added phone field requirement

### 3. URLs (urls.py)
**New URL Patterns Added:**
```python
path('patient/login/', views.patient_login, name='patient-login'),
path('patient/logout/', views.patient_logout, name='patient-logout'),
path('patient/dashboard/', views.patient_dashboard, name='patient-dashboard'),
path('patient/change-password/', views.patient_change_password, name='patient-change-password'),
```

### 4. Templates Created

#### patient-login.html
Patient login page with phone number and password fields.

**Location:** `templates/patient-login.html`

**Features:**
- Mobile number login
- Password field
- Link to registration
- First-time user guidance

#### patient-dashboard.html
Comprehensive patient dashboard.

**Location:** `templates/patient-dashboard.html`

**Features:**
- Patient profile summary
- Quick action cards (Book Emergency, Schedule Appointment)
- Tabbed interface:
  - Upcoming: Shows upcoming cases and appointments
  - In Progress: Shows ongoing cases
  - Completed: Shows completed/past items
  - All: Shows all records
- Change password button
- Logout button

#### patient-change-password.html
Password change interface.

**Location:** `templates/patient-change-password.html`

**Features:**
- Current password verification
- New password with confirmation
- Real-time password match validation
- Back to dashboard link

### 5. Templates Modified

#### index.html
**Changes:**
- Added Mobile Number field
- Added Location field
- Added "Already registered? Login Here" link
- Made phone input required with pattern validation

#### appointment.html
**Changes:**
- Added Mobile Number field
- Added Location field  
- Added Hospital selection dropdown
- Added info about time slot availability
- Added "Login to Dashboard" link

#### home-care.html
**Changes:**
- Made phone field required
- Changed from optional to required address field
- Added login link for registered users

## Database Migration Steps

After updating the models, you need to create and run migrations:

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

**Note:** If you have existing data, you may need to:
1. Backup your database first
2. Handle the new required fields (phone, location) for existing records
3. Or start with a fresh database

## Setup Instructions

### Step 1: Copy All Files

Copy the updated files to your project:

```
models.py → hmsapp/models.py
views.py → hmsapp/views.py
urls.py → hms/urls.py
populate_data.py → hmsapp/management/commands/populate_data.py

# Templates
patient-login.html → templates/patient-login.html
patient-dashboard.html → templates/patient-dashboard.html
patient-change-password.html → templates/patient-change-password.html
index.html → templates/index.html
appointment.html → templates/appointment.html
home-care.html → templates/home-care.html

# Images
aiimsdelhi.jpg → static/images/aiimsdelhi.jpg
maxhospital.jpg → static/images/maxhospital.jpg
safhospi.jpg → static/images/safhospi.jpg
doctor.jpg → static/images/doctor.jpg

# JavaScript
app.js → static/js/app.js
```

### Step 2: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 3: Populate Sample Data

```bash
python manage.py populate_data
```

This will create:
- 5 sample doctors
- 3 sample hospitals with images
- Demo credentials

### Step 4: Test the Features

#### Test Patient Registration and Login:
1. Go to http://127.0.0.1:8000/
2. Fill the emergency registration form with:
   - Name: John Doe
   - Mobile: 9876543210
   - Location: Delhi
   - Symptom: Any
   - Mode: Hospital Emergency
3. Click "BOOK EMERGENCY CASE"
4. You should be redirected to patient dashboard
5. Try logging out and logging back in with:
   - Mobile: 9876543210
   - Password: 9876543210 (same as mobile for first time)

#### Test Password Change:
1. Login to patient dashboard
2. Click "Change Password"
3. Enter current password (your mobile number)
4. Enter new password
5. Confirm new password
6. Submit

#### Test Appointment Booking:
1. Go to http://127.0.0.1:8000/appointment/
2. Fill all fields including mobile and location
3. Select doctor, hospital, date, and time
4. Click "Confirm Booking"
5. Should redirect to patient dashboard

#### Test Double-Booking Prevention:
1. Book an appointment for Dr. Sharma at 10:00 AM
2. Try to book another appointment for Dr. Sharma at 10:00 AM
3. Should see error: "This time slot is already booked"

## Feature Details

### 1. Patient Login System

**How it works:**
- Patient registers via emergency form or appointment booking
- Mobile number becomes the username
- Default password is the mobile number
- Patients can change password later
- Sessions are used to maintain login state

**Session Variables:**
- `patient_id`: Patient's database ID
- `patient_name`: Patient's name
- `patient_phone`: Patient's mobile number

### 2. Patient Dashboard

**Sections:**
1. **Profile Header**: Shows name, phone, location
2. **Statistics**: Total cases and appointments
3. **Quick Actions**: Book Emergency, Schedule Appointment
4. **Tabbed View**:
   - Upcoming: Future appointments and active cases
   - In Progress: Ongoing medical cases
   - Completed: Finished cases and past appointments
   - All: Complete history

### 3. Double-Booking Prevention

**Implementation:**
- Added `unique_together = ['doctor', 'appointment_date', 'appointment_time']` to Appointment model
- Database-level constraint prevents same doctor, date, time combination
- Try-except block catches IntegrityError and shows user-friendly message

### 4. Hospital Assignment

**Auto-Assignment Logic:**
- System automatically assigns nearest/best available hospital
- Based on emergency load (prefers low/medium load)
- Falls back to any active hospital if needed

## API Endpoints

No changes to existing API endpoints. They continue to work as before.

## Security Considerations

1. **Password Hashing**: Using Django's built-in password hashing
2. **Session Management**: Secure session handling
3. **Input Validation**: Pattern validation for phone numbers
4. **CSRF Protection**: Django CSRF tokens on all forms

## Troubleshooting

### Issue: Migration errors with existing data

**Solution:**
```bash
# If you have existing data and migration fails
# Option 1: Fresh start
python manage.py flush  # Clears all data
python manage.py migrate
python manage.py populate_data

# Option 2: Manually update existing records
python manage.py shell
>>> from hmsapp.models import Patient, EmergencyCase, Appointment
>>> # Update existing records with phone numbers
```

### Issue: Images not showing for hospitals

**Solution:**
1. Ensure images are in `static/images/` folder
2. Run `python manage.py collectstatic` if in production
3. Check MEDIA_URL and MEDIA_ROOT in settings.py
4. Verify image paths in populate_data.py

### Issue: "This time slot is already booked" even for different doctors

**Solution:**
- Check that you're selecting different doctors
- Verify the unique_together constraint is properly applied
- Run migrations again if needed

## Testing Checklist

- [ ] Patient can register via emergency form
- [ ] Patient can register via appointment booking
- [ ] Patient can login with mobile + password
- [ ] Patient dashboard shows all cases and appointments
- [ ] Patient can change password
- [ ] Password must match to be accepted
- [ ] Double-booking is prevented
- [ ] Emergency cases show assigned hospital
- [ ] Mobile and location fields are required
- [ ] Sessions persist across page navigation
- [ ] Logout works correctly
- [ ] Hospital images display properly

## Production Deployment Notes

1. **Environment Variables**: Store sensitive data in environment variables
2. **HTTPS**: Always use HTTPS in production
3. **Database**: Use PostgreSQL or MySQL instead of SQLite
4. **Static Files**: Run collectstatic and serve via Nginx/Apache
5. **Sessions**: Configure secure session settings in production

## Additional Notes

### Future Enhancements (Not Implemented Yet)
- Email verification
- SMS OTP for login
- Forgot password functionality
- Profile picture upload
- Appointment reminders
- Real-time case status updates via WebSocket

### Compatibility
- Django 4.0+
- Python 3.8+
- Bootstrap 5.3.2
- Modern browsers (Chrome, Firefox, Safari, Edge)

## Support

For issues or questions:
- Check the Django logs
- Verify all files are in correct locations
- Ensure migrations are applied
- Check browser console for JavaScript errors

---

**Version:** 2.0
**Last Updated:** February 2026
**Author:** Smart Care HMS Development Team
