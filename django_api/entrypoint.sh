#!/bin/bash

set -e

echo "${0}: running migrations."

python manage.py makemigrations
python manage.py migrate

echo "${0}: load data."

python manage.py loaddata api_db.json

echo "${0}: collecting statics."

python manage.py collectstatic || true
cp -r /app/collected_static/. /backend_static/static/ || true

export DJANGO_SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL}
export DJANGO_SUPERUSER_USERNAME=${DJANGO_SUPERUSER_USERNAME}
export DJANGO_SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD}
python manage.py createsuperuser --no-input || true

gunicorn --bind 0.0.0.0:8000 django_api.wsgi