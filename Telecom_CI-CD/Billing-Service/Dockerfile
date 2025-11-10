
# Use official Python base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy the application code
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port your app runs on
EXPOSE 5001

# Run the billing service
CMD ["python", "app.py"]