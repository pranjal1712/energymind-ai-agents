# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Copy and setup startup script
COPY start.sh .
RUN chmod +x start.sh

# Expose port (HF Spaces uses 7860)
EXPOSE 7860

# Run both services
CMD ["./start.sh"]
