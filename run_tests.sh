#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# Load environment variables from .env file
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# Print environment variables for debugging
echo "DB_HOST: $DB_HOST"
echo "DB_USERNAME: $DB_USERNAME"
echo "DB_NAME: $DB_NAME"
echo "DB_PORT: $DB_PORT"

# Check if PostgreSQL client tools are installed
if ! command -v psql &> /dev/null; then
  echo "psql command could not be found"
  exit 1
fi

# Run migrations
echo "Running migrations..."
poetry run python manage.py migrate --settings=wastd.test-settings

# Collect static files
echo "Collecting static files..."
poetry run python manage.py collectstatic --noinput --settings=wastd.test-settings

# Run tests with coverage
echo "Running tests with coverage..."
poetry run coverage run --source='observations' manage.py test observations --settings=wastd.test-settings
poetry run coverage report
poetry run coverage html

echo "Done."
