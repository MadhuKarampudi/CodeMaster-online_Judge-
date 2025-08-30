#!/bin/bash

# Railway startup script
export PORT=${PORT:-8000}

echo "Starting Django Online Judge on port $PORT"

# Run migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput --clear

# Start gunicorn
exec gunicorn online_judge_project.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --timeout 300 \
    --log-level debug \
    --access-logfile - \
    --error-logfile -
