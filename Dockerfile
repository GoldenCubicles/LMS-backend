# Use official Python image
FROM python:3.10-slim

# Install system dependencies for mysqlclient
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the project code
COPY . .

# Run server (change to your actual Django app name if different)
CMD ["gunicorn", "lms_backend.wsgi:application", "--bind", "0.0.0.0:8000"]
