FROM python:3.9-slim

# Install LibreOffice with Python bindings
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice \
    unoconv \
    python3-uno \
    libreoffice-writer \
    fonts-dejavu \
    fonts-liberation \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV UNO_PATH=/usr/lib/libreoffice/program
ENV PYTHONPATH=/usr/lib/python3/dist-packages

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
