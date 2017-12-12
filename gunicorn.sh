#!/bin/bash

# Start Gunicorn server:
echo Starting Gunicorn...
exec gunicorn WebProjects.wsgi:application --bind 0.0.0.0:8081 --workers 3
