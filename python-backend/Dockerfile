FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create model directory
RUN mkdir -p model/vosk-model-small-de-0.15

# Copy application code
COPY . .

# Download Vosk model (if not already present)
RUN if [ ! -d "model/vosk-model-small-de-0.15/am" ]; then \
    apt-get update && apt-get install -y --no-install-recommends wget unzip && \
    wget -q https://alphacephei.com/vosk/models/vosk-model-small-de-0.15.zip && \
    unzip vosk-model-small-de-0.15.zip -d model/ && \
    rm vosk-model-small-de-0.15.zip && \
    apt-get remove -y wget unzip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*; \
    fi

# Expose port
EXPOSE 8765

# Run the application
CMD ["python", "main.py"]