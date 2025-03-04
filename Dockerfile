# Use official Python image (lightweight version)
FROM python:3.9-slim

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    libreoffice \
    unoconv \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements.txt first
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose Cloud Run's required port
EXPOSE 8080

# Set Streamlit config to listen on port 8080
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_ADDRESS="0.0.0.0"

# Run the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
