FROM python:3.9-slim

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice \
    unoconv \
    python3-uno \
    libreoffice-writer \
    libreoffice-calc \
    fonts-dejavu \
    fonts-liberation \
    fonts-noto-core \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Configure environment
ENV STREAMLIT_SERVER_PORT=8080
ENV UNO_PATH=/usr/lib/libreoffice/program
ENV PYTHONPATH=/usr/lib/python3/dist-packages

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=30s --start-period=30s \
  CMD curl -f http://localhost:8080/_stcore/health || exit 1

# Start services
CMD (sleep 20 && unoserver --port 2002 --interface 0.0.0.0 &) && \
    streamlit run app.py --server.port 8080 --server.address 0.0.0.0
