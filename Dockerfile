# Use an official lightweight Python image
FROM python:3.10-slim

# Prevent interactive prompts during apt installs
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies for pdfkit + wkhtmltopdf + emoji fonts
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    xfonts-75dpi \
    xfonts-base \
    fonts-dejavu \
    fonts-noto-color-emoji \
    libxrender1 \
    libfontconfig1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency file first (better layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Streamlit will run in headless mode
ENV STREAMLIT_SERVER_HEADLESS=true
ENV PYTHONUNBUFFERED=1

# Expose Streamlit default port
EXPOSE 8501

# Command to run the app on Render
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
