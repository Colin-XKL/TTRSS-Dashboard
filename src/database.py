import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

load_dotenv()

def get_database_url() -> str:
    """
    Constructs the database URL from environment variables.
    Supports both PostgreSQL and MySQL.
    """
    db_type = os.getenv("TTRSS_DB_TYPE", "pgsql")  # pgsql or mysql
    user = os.getenv("TTRSS_DB_USER", "postgres")
    password = os.getenv("TTRSS_DB_PASS", "password")
    host = os.getenv("TTRSS_DB_HOST", "localhost")
    port = os.getenv("TTRSS_DB_PORT", "5432")
    db_name = os.getenv("TTRSS_DB_NAME", "ttrss")

    if db_type == "mysql":
        # PyMySQL driver for MySQL
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}"
    else:
        # Psycopg2 driver for PostgreSQL
        return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}"

_engine = None

def get_engine():
    global _engine
    if _engine is None:
        db_url = get_database_url()
        _engine = create_engine(db_url, pool_pre_ping=True)
    return _engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=None)

def get_db() -> Session:
    """
    Dependency to get a DB session.
    Ensure to close it after use.
    """
    engine = get_engine()
    SessionLocal.configure(bind=engine)
    session = SessionLocal()
    try:
        return session
    except Exception:
        session.close()
        raise
