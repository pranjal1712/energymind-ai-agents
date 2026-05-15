FROM python:3.11-slim

# Set working directory to project root (this allows us to import .backend)
WORKDIR /app

# Install system dependencies (needed for some python packages like psycopg2)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from root and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install production server
RUN pip install gunicorn uvicorn

# Copy entire project directory
COPY . .

# Expose port
EXPOSE 8000

# Command to run the application using Gunicorn for production
# Use $PORT so Render can assign the port dynamically
CMD ["sh", "-c", "gunicorn -w 2 -k uvicorn.workers.UvicornWorker backend.main:app --bind 0.0.0.0:${PORT:-8000} --timeout 120"]
