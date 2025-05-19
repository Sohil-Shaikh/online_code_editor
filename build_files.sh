#!/bin/bash

# Install Python dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Create a .env file with production settings
echo "DEBUG=False" > .env
echo "SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')" >> .env
echo "ALLOWED_HOSTS=*" >> .env 