web: python manage.py migrate --noinput && python manage.py collectstatic --noinput --clear && gunicorn online_judge_project.wsgi:application --bind 0.0.0.0:8000 --workers 1 --timeout 300
