FROM python:3.11-slim

# Copy the uv binary from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency configuration
COPY services/digifax-api/pyproject.toml services/digifax-api/uv.lock* /app/

# Install dependencies using uv
RUN uv sync --frozen --no-install-project --no-dev

# Copy application source
COPY services/digifax-api/src /app/src

# Set PYTHONPATH to include /app
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Start server
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
