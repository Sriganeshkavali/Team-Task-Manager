FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required for certain Python libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Grant execution permissions to our startup script
RUN chmod +x start.sh

# Expose the standard routing port
EXPOSE 8080

# Execute the services
CMD ["./start.sh"]
