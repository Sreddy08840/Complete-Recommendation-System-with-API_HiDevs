
# Use official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create data directory for SQLite database
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
