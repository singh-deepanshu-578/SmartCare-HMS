#!/usr/bin/env python3
"""
Quick setup script for HMS Django project
Run this after creating your Django project
"""

import os
import shutil
import sys


def create_directory_structure():
    """Create the required directory structure"""
    dirs = [
        'static/css',
        'static/js',
        'static/images',
        'templates',
        'media',
        'hmsapp/management/commands',
    ]
    
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"✓ Created: {d}")


def create_init_files():
    """Create __init__.py files"""
    init_files = [
        'hmsapp/management/__init__.py',
        'hmsapp/management/commands/__init__.py',
    ]
    
    for f in init_files:
        with open(f, 'w') as file:
            file.write('')
        print(f"✓ Created: {f}")


def main():
    print("=" * 50)
    print("Smart Care HMS - Django Setup")
    print("=" * 50)
    print()
    
    print("Creating directory structure...")
    create_directory_structure()
    print()
    
    print("Creating __init__.py files...")
    create_init_files()
    print()
    
    print("=" * 50)
    print("Setup Complete!")
    print("=" * 50)
    print()
    print("Next steps:")
    print("1. Copy the generated Python files to your project:")
    print("   - models.py → hmsapp/models.py")
    print("   - views.py → hmsapp/views.py")
    print("   - urls.py → hms/urls.py")
    print("   - admin.py → hmsapp/admin.py")
    print("   - apps.py → hmsapp/apps.py")
    print("   - forms.py → hmsapp/forms.py")
    print("   - context_processors.py → hmsapp/context_processors.py")
    print("   - populate_data.py → hmsapp/management/commands/populate_data.py")
    print()
    print("2. Copy templates to templates/ folder")
    print("3. Copy static files to static/ folder:")
    print("   - style.css → static/css/style.css")
    print("   - app.js → static/js/app.js")
    print("   - images → static/images/")
    print()
    print("4. Update settings.py (see INTEGRATION_GUIDE.md)")
    print()
    print("5. Run migrations:")
    print("   python manage.py makemigrations")
    print("   python manage.py migrate")
    print()
    print("6. Populate sample data:")
    print("   python manage.py populate_data")
    print()
    print("7. Create superuser:")
    print("   python manage.py createsuperuser")
    print()
    print("8. Run server:")
    print("   python manage.py runserver")


if __name__ == '__main__':
    main()
