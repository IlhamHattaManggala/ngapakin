# syntax=docker/dockerfile:1
FROM python:3.11-slim

LABEL maintainer="Ilham Hatta Manggala <ilhamhattamanggala123@gmail.com>"
LABEL description="Official Docker image for Larapak MVC Framework & NgapakIn Language"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    APP_PORT=8000 \
    APP_HOST=0.0.0.0

# Install minimal OS dependencies for database drivers and system tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy framework files and install
COPY . /tmp/ngapakin
RUN pip install --no-cache-dir "/tmp/ngapakin[all]" || pip install --no-cache-dir /tmp/ngapakin \
    && rm -rf /tmp/ngapakin

# Expose web server port
EXPOSE 8000

# Default entrypoint and command
ENTRYPOINT ["ngapakin"]
CMD ["serve", "8000"]

