# apps/api/Dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn celery redis

# Copy the rest of the application
COPY src/ .

# Expose port
EXPOSE 5000

# Start script
CMD ["python", "app.py"]
