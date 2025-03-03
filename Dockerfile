# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy the project files into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose a port (use the one your Streamlit app runs on)
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "app.py"]
