FROM python:3.9-slim

# Install Linux dependencies (excludes docx2pdf)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice \
    unoconv \
    python3-uno \
    libreoffice-writer \
    fonts-dejavu \
    fonts-liberation \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD (sleep 20 && unoserver --port 2002 &) && \
    streamlit run app.py --server.port 8080 --server.address 0.0.0.0
