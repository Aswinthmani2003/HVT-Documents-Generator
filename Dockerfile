FROM python:3.9-slim

# Install LibreOffice with PyUNO and fonts
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice \
    unoconv \
    libreoffice-writer \
    libreoffice-calc \
    libreoffice-impress \
    libreoffice-style-breeze \
    fonts-dejavu \
    fonts-liberation \
    fonts-noto-core \
    fonts-noto-extra \
    python3-uno \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080
ENV STREAMLIT_SERVER_PORT=8080

CMD (unoserver --port 2002 &) && \
    streamlit run app.py --server.port 8080 --server.address 0.0.0.0
