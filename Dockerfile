# Use an optimized base image with LibreOffice pre-installed
FROM ghcr.io/courville/uno-api:latest

# Set working directory
WORKDIR /app

# Copy only requirements.txt first to leverage caching
COPY requirements.txt .

# Install dependencies separately to avoid reinstalling every time
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application after installing dependencies
COPY . .

# Expose port 8501 for Streamlit
EXPOSE 8501

# Start LibreOffice service in the background and launch Streamlit
CMD (unoserver --port 2002 &) && streamlit run app.py --server.port=8501 --server.address=0.0.0.0
