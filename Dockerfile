# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=online_judge_project.settings

# Set the working directory in the container
WORKDIR /app

# Install system dependencies including compilers for code execution
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    default-jdk \
    sqlite3 \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create necessary directories with proper permissions
RUN mkdir -p /app/data /app/staticfiles /app/media

# Create a non-root user for security (before collectstatic)
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app/data

# Switch to non-root user
USER appuser

# Collect static files as non-root user
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run the application with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "online_judge_project.wsgi:application"]