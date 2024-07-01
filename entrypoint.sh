#!/bin/sh

# entrypoint.sh

set -e

./wait-for-db.sh db

python manage.py migrate

if [ "$DJANGO_SUPERUSER_USERNAME" ]; then
    ./createsuperuser.sh || true
fi

python manage.py collectstatic --noinput

exec "$@"
