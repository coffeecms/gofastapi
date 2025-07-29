# Dockerfile for GoFastAPI
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Go
ENV GO_VERSION=1.21.0
RUN curl -fsSL https://golang.org/dl/go${GO_VERSION}.linux-amd64.tar.gz | tar -C /usr/local -xzf -
ENV PATH="/usr/local/go/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy Go module files
COPY go.mod go.sum ./
RUN go mod download

# Copy Python requirements
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Build Go binaries
RUN python scripts/build.py --go-only

# Build Python package
RUN python scripts/build.py --python-only

# Install the package
RUN pip install dist/*.whl

# Production stage
FROM python:3.11-slim as production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r gofastapi && useradd -r -g gofastapi gofastapi

# Set working directory
WORKDIR /app

# Copy built application from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app/gofastapi_server* ./

# Copy application files
COPY app/ ./app/
COPY gofastapi.toml ./

# Change ownership to non-root user
RUN chown -R gofastapi:gofastapi /app

# Switch to non-root user
USER gofastapi

# Expose ports
EXPOSE 8000 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["gofastapi", "run", "app:app", "--host", "0.0.0.0", "--port", "8000"]

# Development stage
FROM builder as development

# Install development dependencies
RUN pip install --no-cache-dir -r requirements-dev.txt

# Install the package in development mode
RUN pip install -e .

# Expose ports (including debug ports)
EXPOSE 8000 9090 5678

# Development command with hot-reload
CMD ["gofastapi", "dev", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
