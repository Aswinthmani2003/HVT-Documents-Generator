# Use official Python image
FROM python:3.10

# Set working directory
WORKDIR /app

# Copy files to container
COPY . /app

# Upgrade pip
RUN pip install --upgrade pip

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8080 for Cloud Run
EXPOSE 8080

# Run the Streamlit app on the correct port
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
