# TTRSS Dashboard

A modern, elegant dashboard for analyzing your Tiny Tiny RSS (TT-RSS) data, built with [Streamlit](https://streamlit.io).

## Features

- **Direct Database Integration**: Connects directly to your TT-RSS database (PostgreSQL or MySQL) for real-time stats.
- **Interactive Analytics**:
    - Global statistics (Total Feeds, Unread Count, Labels, Starred).
    - Feed distribution by category.
    - Word frequency analysis (Word Cloud & Charts) for individual feeds.
    - Recent article explorer.
- **Modern UI**: Clean interface powered by Streamlit and Plotly.

## Prerequisites

- Python 3.12+
- [Poetry](https://python-poetry.org/) (for dependency management)
- Access to a running TT-RSS database (PostgreSQL or MySQL).

## Configuration

1.  Clone the repository.
2.  Copy `.env.example` to `.env`:
    ```bash
    cp .env.example .env
    ```
3.  Edit `.env` and fill in your database connection details:

    ```ini
    TTRSS_DB_TYPE=pgsql          # or 'mysql'
    TTRSS_DB_HOST=localhost
    TTRSS_DB_PORT=5432
    TTRSS_DB_NAME=ttrss
    TTRSS_DB_USER=your_user
    TTRSS_DB_PASS=your_password
    ```

## Running Locally
0. You can map your running ttrss db via ssh port forwarding.
```bash
ssh -L 5432:localhost:5432 your_server
```

1.  **Install dependencies**:
    ```bash
    poetry install
    ```

2.  **Run the application**:
    ```bash
    poetry run streamlit run src/ui/main.py
    ```

3.  Open your browser at `http://localhost:8501`.

## Running with Docker

1.  **Build the image**:
    ```bash
    docker build -t ttrss-dashboard .
    ```

2.  **Run the container**:
    ```bash
    docker run -d -p 8501:8501 --env-file .env ttrss-dashboard
    ```


