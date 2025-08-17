# Use Python slim image instead of full Ubuntu
FROM python:3.10-slim

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies (wkhtmltopdf + fonts for emoji/PDF)
RUN apt-get update && apt-get install -y --no-install-recommends \
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

# Copy requirements first (for Docker cache efficiency)
COPY requirements.txt .

# Upgrade pip & install dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Environment variables for Streamlit & Prophet
ENV STREAMLIT_SERVER_HEADLESS=true
ENV PYTHONUNBUFFERED=1
ENV CMDSTANPY_CACHE=/tmp/cmdstan

# Expose Streamlit default port
EXPOSE 8501

# Run Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
