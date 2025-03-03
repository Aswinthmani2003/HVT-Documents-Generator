# Dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libreoffice \
    libnss3 \
    libxinerama1 \
    libglu1-mesa \
    libsm6 \
    libx11-xcb1 \
    libxcb-glx0 \
    libxrender1 \
    libfontconfig1 \
    libdbus-1-3 \
    libxt6 \
    libxext6 \
    libcups2 \
    libxrandr2 \
    libgtk-3-0 \
    libgbm1 \
    ttf-mscorefonts-installer \
    fonts-dejavu \
    fonts-freefont-ttf \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && fc-cache -f -v

# Accept Microsoft fonts EULA
RUN echo "ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true" | debconf-set-selections

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
