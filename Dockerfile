# Updated Dockerfile
FROM python:3.9-slim

# Install LibreOffice and dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libreoffice \
    libssl-dev \
    fonts-liberation \
    libnss3 \
    libx11-xcb1 \
    libxcb1 \
    libxext6 \
    libxrender1 \
    libxt6 \
    xdg-utils && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
