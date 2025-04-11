#!/bin/bash

echo "Running setup tasks..."

# Make sure migrations exist
python manage.py makemigrations devices

# Run migrations
python manage.py migrate

# Seed data
python manage.py seed_devices

# Create superuser if not exists
echo "from django.contrib.auth import get_user_model; \
User = get_user_model(); \
User.objects.filter(username='admin').exists() or \
User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')" | python manage.py shell

# Run the default command
exec "$@"
