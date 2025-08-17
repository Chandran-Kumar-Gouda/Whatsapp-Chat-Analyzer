# Use Ubuntu 22.04 (stable, wkhtmltopdf available)
FROM ubuntu:22.04

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install Python, pip, wkhtmltopdf, and fonts
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    wkhtmltopdf \
    xfonts-75dpi \
    xfonts-base \
    fonts-dejavu \
    fonts-noto-color-emoji \
    libxrender1 \
    libfontconfig1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Set python3.10 as default python
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1

# Set working directory
WORKDIR /app

# Copy dependency file
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

# Run Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
