FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose the port your application runs on
EXPOSE 8000

# Start the application
# Adjust this command based on how you start your Python app
CMD ["python", "app.py"]