# Use a base image (Python example)
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose a port (if your app runs a server)
EXPOSE 8080

# Define the startup command (modify based on your project entry point)
CMD ["python", "app.py"]
