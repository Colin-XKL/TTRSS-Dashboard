FROM python:3.12-slim

# Install system dependencies
# libpq-dev is required for psycopg2 (PostgreSQL)
# gcc and python3-dev are often needed for compiling certain python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    python3-dev \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

RUN fc-cache -fv

# Install Poetry
RUN pip install poetry

# Configure Poetry to not create virtual env inside Docker
# (since we are already inside a container)
RUN poetry config virtualenvs.create false

WORKDIR /app

# Copy dependency definitions
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Copy project files
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Add /app to PYTHONPATH so imports like "from src..." work
ENV PYTHONPATH="${PYTHONPATH}:/app"

# Run the application
CMD ["streamlit", "run", "src/ui/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
