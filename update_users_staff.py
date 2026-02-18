#!/usr/bin/env python
"""
Script to update all existing users to have is_staff=True
Run this with: python update_users_staff.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DocumentGenerator.settings')
django.setup()

from backendapp.models import User

# Update all users to have is_staff=True
updated_count = User.objects.filter(is_staff=False).update(is_staff=True)
print(f"✅ Updated {updated_count} users to have is_staff=True")

# Show all users
all_users = User.objects.all()
print(f"\n📋 Total users: {all_users.count()}")
for user in all_users:
    print(f"  - {user.username or user.email}: is_staff={user.is_staff}, role={user.role}")
