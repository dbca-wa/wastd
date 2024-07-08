#!/bin/sh

# createentereruser.sh

set -e

# Create the Enterer user
python manage.py shell << END
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.utils import IntegrityError

User = get_user_model()

try:
    user = User.objects.create_user(
        username='$DJANGO_ENTERER_USERNAME',
        email='$DJANGO_ENTERER_EMAIL',
        password='$DJANGO_ENTERER_PASSWORD',
        name='Volunteer',
        role='Data Enterer',
    )
    
    enterer_group, created = Group.objects.get_or_create(name='Enterer')
    user.groups.add(enterer_group)
    
    print("Enterer user created successfully")
except IntegrityError:
    print("Enterer user already exists")
except Group.DoesNotExist:
    print("Enterer group does not exist. Please run migrations first.")
except Exception as e:
    print(f"Error creating Enterer user: {str(e)}")
END