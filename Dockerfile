# Official lightweight Python image
FROM python:3.11-slim

# Ensure output is sent straight to terminal (no buffering)
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . ./

# copy and enable entrypoint script
COPY scripts/docker_entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker_entrypoint.sh

# Run migrations and collect static files during build to catch errors early
# (these will also run at startup via entrypoint script if desired)
RUN python manage.py migrate --noinput
RUN python manage.py collectstatic --noinput

# Expose port the app runs on
EXPOSE 8000

# Run entrypoint script to prepare environment then start gunicorn
ENTRYPOINT ["docker_entrypoint.sh"]

# Default command: use gunicorn for production
CMD ["gunicorn", "DocumentGenerator.wsgi:application", "--bind", "0.0.0.0:8000"]
