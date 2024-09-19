#!/bin/sh

# createentereruser.sh

set -e

# Create the Data Entry user
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
    
    # Add user to Tagging Data Entry group
    tagging_data_entry_group, created = Group.objects.get_or_create(name='WAMTRAM2_VOLUNTEER')
    user.groups.add(tagging_data_entry_group)
    
    print("Data Entry user created successfully and added to Tagging Data Entry group")
except IntegrityError:
    print("Data Entry user already exists")
except Group.DoesNotExist:
    print("Tagging Data Entry group does not exist. Please check your group configurations.")
except Exception as e:
    print(f"Error creating Data Entry user: {str(e)}")
END