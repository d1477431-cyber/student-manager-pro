web: python manage.py migrate --no-input && python manage.py collectstatic --no-input && gunicorn studentmanager.wsgi --bind 0.0.0.0:$PORT
