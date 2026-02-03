# Django HMS Integration Guide

## Complete Guide to Integrate CSS and JS in Django

---

## 1. Project Structure

Your Django project should have this structure:

```
hms_project/
├── hms/                      # Project folder (settings, urls, wsgi)
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── hmsapp/                   # Your app folder
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── context_processors.py
│   └── management/
│       └── commands/
│           └── populate_data.py
│
├── templates/                # Global templates folder
│   ├── base.html
│   ├── index.html
│   ├── patient.html
│   ├── doctor.html
│   ├── doctor-dashboard.html
│   ├── appointment.html
│   ├── emergency-queue.html
│   ├── home-care.html
│   └── home-tracking.html
│
├── static/                   # Static files folder
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── app.js
│   └── images/
│       └── doctor.jpg
│
├── media/                    # User-uploaded files
├── db.sqlite3
└── manage.py
```

---

## 2. Settings.py Configuration

### 2.1 Static Files Configuration

Add these settings to your `settings.py`:

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"

# Where Django looks for static files during development
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Where static files are collected during deployment
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files (User uploads)
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
```

### 2.2 Templates Configuration

```python
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'],  # Global templates folder
        "APP_DIRS": True,  # Also check app templates folders
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.static",
                "django.template.context_processors.media",
                # Custom context processors
                "hmsapp.context_processors.hms_stats",
                "hmsapp.context_processors.doctor_session",
            ],
        },
    },
]
```

### 2.3 Installed Apps

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    'hmsapp',  # Your app
]
```

---

## 3. How to Use Static Files in Templates

### 3.1 Load Static Template Tag

At the top of every template that uses static files:

```html
{% load static %}
```

### 3.2 Reference CSS Files

```html
<!-- In <head> section -->
<link rel="stylesheet" href="{% static 'css/style.css' %}" />
```

### 3.3 Reference JavaScript Files

```html
<!-- Before closing </body> tag -->
<script src="{% static 'js/app.js' %}"></script>
```

### 3.4 Reference Images

```html
<img src="{% static 'images/doctor.jpg' %}" alt="Doctor" />
```

### 3.5 Complete Example (base.html)

```html
<!DOCTYPE html>
{% load static %}
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>{% block title %}Smart Care HMS{% endblock %}</title>

    <!-- External CSS (CDN) -->
    <link
      href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css"
      rel="stylesheet"
    />

    <!-- Your Custom CSS -->
    <link rel="stylesheet" href="{% static 'css/style.css' %}" />

    {% block extra_css %}{% endblock %}
  </head>
  <body>
    {% block content %}{% endblock %}

    <!-- External JS (CDN) -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>

    <!-- Your Custom JS -->
    <script src="{% static 'js/app.js' %}"></script>

    {% block extra_js %}{% endblock %}
  </body>
</html>
```

---

## 4. URL Configuration for Static/Media Files

### 4.1 Development (settings.py)

```python
DEBUG = True
```

Django automatically serves static files in development.

### 4.2 urls.py (for development)

```python
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # ... your other URLs
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### 4.3 Production

In production, use a web server (Nginx/Apache) to serve static files:

```bash
# Collect all static files
python manage.py collectstatic
```

---

## 5. Template Inheritance

### 5.1 Base Template (templates/base.html)

```html
{% load static %}
<!DOCTYPE html>
<html>
  <head>
    <title>{% block title %}Default Title{% endblock %}</title>
    <link rel="stylesheet" href="{% static 'css/style.css' %}" />
  </head>
  <body>
    <nav><!-- Navbar --></nav>

    {% block content %}{% endblock %}

    <footer><!-- Footer --></footer>
    <script src="{% static 'js/app.js' %}"></script>
  </body>
</html>
```

### 5.2 Child Template (templates/index.html)

```html
{% extends 'base.html' %} {% load static %} {% block title %}Home | Smart Care
HMS{% endblock %} {% block content %}
<h1>Welcome to Smart Care HMS</h1>
<img src="{% static 'images/doctor.jpg' %}" alt="Doctor" />
{% endblock %}
```

---

## 6. Setup Steps

### Step 1: Create Project Structure

```bash
# Create static directories
mkdir -p static/css static/js static/images

# Create templates directory
mkdir templates

# Create media directory
mkdir media
```

### Step 2: Copy Files

```bash
# Copy CSS
cp /path/to/style.css static/css/

# Copy JS
cp /path/to/app.js static/js/

# Copy images
cp /path/to/doctor.jpg static/images/

# Copy templates
cp /path/to/*.html templates/
```

### Step 3: Update Templates

Replace all static references in templates:

**Before:**

```html
<link rel="stylesheet" href="css/style.css" />
<script src="js/app.js"></script>
<img src="doctor.jpg" />
```

**After:**

```html
{% load static %}
<link rel="stylesheet" href="{% static 'css/style.css' %}" />
<script src="{% static 'js/app.js' %}"></script>
<img src="{% static 'images/doctor.jpg' %}" />
```

### Step 4: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Populate Sample Data

```bash
python manage.py populate_data
```

### Step 6: Create Superuser

```bash
python manage.py createsuperuser
```

### Step 7: Run Development Server

```bash
python manage.py runserver
```

---

## 7. Key URL Mappings

| URL                  | View               | Description                           |
| -------------------- | ------------------ | ------------------------------------- |
| `/`                  | `index`            | Home page with emergency registration |
| `/patient/`          | `patient`          | Patient portal                        |
| `/patient/register/` | `patient_register` | Submit emergency case                 |
| `/doctor/`           | `doctor`           | Doctor login                          |
| `/doctor/dashboard/` | `doctor_dashboard` | Doctor dashboard                      |
| `/appointment/`      | `appointment`      | Book appointment                      |
| `/emergency-queue/`  | `emergency_queue`  | View emergency queue                  |
| `/home-care/`        | `home_care`        | Request home care                     |
| `/home-tracking/`    | `home_tracking`    | Track doctor arrival                  |
| `/admin/`            | Django Admin       | Admin panel                           |

---

## 8. Demo Credentials

### Doctors

- **Dr. Sharma**: `sharma123`
- **Dr. Mehta**: `mehta123`
- **Dr. Verma**: `verma123`

### Admin

Create your own superuser with:

```bash
python manage.py createsuperuser
```

---

## 9. Quick Commands Reference

```bash
# Run server
python manage.py runserver

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Populate sample data
python manage.py populate_data

# Collect static files (production)
python manage.py collectstatic

# Open Django shell
python manage.py shell
```

---

## 10. Troubleshooting

### Static files not loading?

1. Check `STATIC_URL` and `STATICFILES_DIRS` in settings.py
2. Ensure `{% load static %}` is at the top of templates
3. Use `{% static 'path/to/file' %}` syntax
4. Run `python manage.py collectstatic`

### Templates not found?

1. Check `TEMPLATES['DIRS']` in settings.py
2. Verify template file names match view references

### Database errors?

1. Run `python manage.py makemigrations`
2. Run `python manage.py migrate`

---

## 11. Production Deployment Checklist

- [ ] Set `DEBUG = False`
- [ ] Set proper `ALLOWED_HOSTS`
- [ ] Run `collectstatic`
- [ ] Configure web server (Nginx/Apache) for static files
- [ ] Use environment variables for SECRET_KEY
- [ ] Set up proper database (PostgreSQL/MySQL)
- [ ] Configure SSL/HTTPS
