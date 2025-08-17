# Use an official lightweight Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (wkhtmltopdf, fonts, etc.)
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    fonts-dejavu \
    fonts-noto-color-emoji \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose port for Streamlit
EXPOSE 8080

# Command to run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.headless=true"]
