#!/bin/sh

# createsuperuser.sh

set -e

# Load only DJANGO_SUPERUSER_* vars from .env (ignore other entries like Driver=...)
if [ -f ".env" ]; then
  while IFS= read -r line; do
    case "$line" in
      ''|\#*) continue ;;
    esac
    case "$line" in
      DJANGO_SUPERUSER_*=*)
        key="${line%%=*}"
        value="${line#*=}"
        value="${value%$'\r'}"
        export "$key=$value"
        ;;
    esac
  done < ./.env
fi

python manage.py shell <<'END'
import os
from django.contrib.auth import get_user_model

username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
name = os.environ.get("DJANGO_SUPERUSER_NAME", "WASTD Admin")

if not username or not email or not password:
    raise SystemExit("DJANGO_SUPERUSER_USERNAME/EMAIL/PASSWORD 必须在 .env 中设置。")

User = get_user_model()
user, created = User.objects.get_or_create(username=username, defaults={"email": email})
user.email = email
user.name = name
user.is_staff = True
user.is_superuser = True
user.set_password(password)
user.save()

action = "created" if created else "updated"
print(f"Superuser {username} {action} and password reset.")
END
