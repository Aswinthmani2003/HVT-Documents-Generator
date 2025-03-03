# Updated Dockerfile
FROM python:3.9-slim

# Install LibreOffice and dependencies
# Add to existing Dockerfile
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libxinerama1 \
    libdbus-glib-1-2 \
    libglu1 \
    libsm6 \
    libxrender1 \
    libfontconfig1 \
    libx11-6

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
