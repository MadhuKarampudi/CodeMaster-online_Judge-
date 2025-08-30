web: python manage.py migrate --noinput && python manage.py collectstatic --noinput --clear && gunicorn online_judge_project.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
