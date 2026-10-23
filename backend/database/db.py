import os
from contextlib import contextmanager
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent / ".env")

_pool = None

def init_pool():
    global _pool
    if _pool in None:
        _pool = pool.ThreadedConnectionPool(
            minconn= 1,
            maxconn= 10,
            host = os.getenv("DB_HOST", "localhost"),
            port = int(os.getenv("DB_PORT", 5432)),
            dbname = os.getenv("DB_NAME"),
            user = os.getenv("DB_USER"),
            password = os.getenv("DB_PASSWORD")
        )

def close():
    if _pool is not None:
        _pool.closeall()
        _pool = None


@contextmanager
def get_conn():
    if _pool is None:
        init_pool()
    conn = _pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        _pool.putconn(conn)


