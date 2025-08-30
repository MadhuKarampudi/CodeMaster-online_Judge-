release: python manage.py migrate --noinput && python manage.py collectstatic --noinput --clear
web: gunicorn online_judge_project.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --timeout 300 --log-level debug --access-logfile - --error-logfile -
