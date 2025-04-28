# Use official Python slim image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install system dependencies (if any are needed beyond base python)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#  && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Run the FastAPI app with Uvicorn
# Use 0.0.0.0 to be accessible from outside the container
# Add --reload for development if needed, but remove for production
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
