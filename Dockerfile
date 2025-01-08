# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory to /app
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y gcc libpq-dev docker.io && \
    pip install --upgrade pip

# Copy requirements and install them
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# Copy the project into the container
COPY . /app/

# Set the working directory to /app/cron_project for running the Django app
WORKDIR /app/cron_project

# Expose necessary ports
EXPOSE 8000

# Default command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

RUN pip install psycopg2-binary