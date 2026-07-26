FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for packages like psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose FastAPI backend port
EXPOSE 8000

# Start server
CMD ["python", "run.py"]
