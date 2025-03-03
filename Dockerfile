FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    TEMPLATES_DIR=/app/templates

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libreoffice-writer \
    libreoffice-headless \
    fonts-dejavu \
    fonts-liberation \
    fonts-noto-cjk \
    fonts-noto-core \
    fonts-freefont-ttf \
    libxinerama1 \
    libdbus-glib-1-2 \
    libcairo2 \
    libgl1 \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy ALL files including templates
COPY . .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 8080

CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
