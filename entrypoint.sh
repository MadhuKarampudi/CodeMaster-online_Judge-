#!/bin/bash

# Wait for database to be ready
echo "Setting up database..."

# Run migrations
python manage.py migrate --noinput

# Create superuser if it doesn't exist
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@example.com').exists():
    User.objects.create_superuser(email='admin@example.com', password='admin123')
    print('Superuser created: admin@example.com/admin123')
else:
    print('Superuser already exists')
"

# Start the application
exec "$@"
