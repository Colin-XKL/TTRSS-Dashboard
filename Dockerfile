# Stage 1: Builder
FROM python:3.12-slim AS builder

WORKDIR /app

# Install system dependencies for building packages
# build-essential: for gcc (needed for wordcloud, etc.)
# libpq-dev: for building psycopg2 (if not binary) or other db drivers
# python3-dev: for python header files
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy dependency definitions
COPY pyproject.toml poetry.lock* ./

# Configure poetry to create venv in project
RUN poetry config virtualenvs.in-project true

# Install dependencies (only main dependencies, no dev)
RUN poetry install --no-interaction --no-ansi --no-root --only main

# Stage 2: Runner
FROM python:3.12-slim AS runner

WORKDIR /app

# Install runtime dependencies
# fontconfig, fonts-noto-cjk, fonts-wqy-zenhei: for Chinese font support in visualizations
# libpq5: runtime library for PostgreSQL (good to have for consistency)
RUN apt-get update && apt-get install -y \
    fontconfig \
    fonts-noto-cjk \
    fonts-wqy-zenhei \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Update font cache
RUN fc-cache -fv

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY . .

# Set environment variables
# Add venv/bin to PATH so we can run 'streamlit' directly
ENV PATH="/app/.venv/bin:$PATH"
# Add /app to PYTHONPATH
ENV PYTHONPATH="${PYTHONPATH}:/app"

# Expose Streamlit port
EXPOSE 8501

# Run the application
CMD ["streamlit", "run", "src/ui/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
