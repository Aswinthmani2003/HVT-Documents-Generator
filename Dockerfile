# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Install LibreOffice and dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice \
    unoconv \
    libreoffice-writer \
    fonts-liberation \
    fonts-dejavu \
    fonts-noto-core \
    fonts-noto-extra \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY . .

# Expose port for Streamlit
EXPOSE 8501

# Start unoserver and Streamlit
CMD (unoserver --port 2002 &) && streamlit run app.py --server.port 8501 --server.address 0.0.0.0
