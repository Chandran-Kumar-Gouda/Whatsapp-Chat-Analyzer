FROM python:3.9-slim

# Install wkhtmltopdf and emoji fonts
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    libxrender1 \
    libxext6 \
    libfontconfig1 \
    fonts-noto-color-emoji \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy all project files
COPY . .

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
