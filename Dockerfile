# Use the official Python image from Docker Hub
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (Tesseract and others)
RUN apt-get update && \
    apt-get install -y tesseract-ocr && \
    apt-get clean

# Copy the current directory contents into the container at /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app will run on
EXPOSE 10000

# Define the command to run your app
CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=10000"]
