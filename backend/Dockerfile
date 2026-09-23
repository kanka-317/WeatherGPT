FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies (build-essential, libpq-dev for psycopg2/geo packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY . /app/

# Expose port
EXPOSE 8000

# Default command runs alembic migrations and starts uvicorn on dynamic PORT
CMD ["sh", "-c", "alembic upgrade head || true && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
