web: python manage.py migrate --no-input && python manage.py collectstatic --no-input && python manage.py ensure_superuser && daphne studentmanager.asgi:application --bind 0.0.0.0 --port $PORT
