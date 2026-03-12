#!/bin/sh

# entrypoint script for Docker container
set -e

# wait for db if needed (optional: add logic with e.g. "wait-for" or similar)

# run migrations and collect static files
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# execute the container's main process (CMD)
exec "$@"
