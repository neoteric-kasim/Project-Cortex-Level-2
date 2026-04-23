# Use Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Prevent Python from buffering logs
ENV PYTHONUNBUFFERED=1

# Install system deps (optional but safe)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project (backend + static frontend)
COPY . .

# Expose port
EXPOSE 8000

# Start FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]