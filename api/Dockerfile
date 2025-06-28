## Dockerfile for FastAPI application with pyodbc and Azure SQL Database
# Stage 1 — Build
FROM python:3.11-slim as builder
WORKDIR /app
# System packages for building pyodbc and dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    unixodbc-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install pip dependencies into a temporary directory
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt

# Stage 2 — Runtime
FROM python:3.11-slim
WORKDIR /app
# Install only runtime system dependencies
RUN apt-get update && apt-get install -y \
    unixodbc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local
COPY . .
# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
