import os
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from flask_sqlalchemy import SQLAlchemy

# Shared SQLAlchemy metadata and connection object for the Flask app.
db = SQLAlchemy()


def _ensure_postgres_scheme(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


def _ensure_sslmode(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme.startswith("postgres"):
        query = dict(parse_qsl(parsed.query, keep_blank_values=True))
        if query.get("sslmode") != "require":
            query["sslmode"] = "require"
            parsed = parsed._replace(query=urlencode(query, doseq=True))
    return urlunparse(parsed)


def get_database_uri() -> str:
    database_url = os.environ.get("DATABASE_URL") or os.environ.get("SQLALCHEMY_DATABASE_URI")
    if not database_url:
        print("DATABASE WARNING: DATABASE_URL environment variable is not set. Falling back to local SQLite for development.")
        return "sqlite:///agrosmart.db"

    database_url = _ensure_postgres_scheme(database_url.strip())
    database_url = _ensure_sslmode(database_url)
    return database_url


def configure_app(app):
    database_url = get_database_uri()
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
    }

    if database_url.startswith("postgresql://"):
        app.config["SQLALCHEMY_ENGINE_OPTIONS"].update(
            {
                "connect_args": {"sslmode": "require"},
                "pool_size": int(os.environ.get("DB_POOL_SIZE", 5)),
                "max_overflow": int(os.environ.get("DB_MAX_OVERFLOW", 10)),
                "pool_timeout": int(os.environ.get("DB_POOL_TIMEOUT", 30)),
            }
        )

    app.config["UPLOADS_BASE_URL"] = os.environ.get("UPLOADS_BASE_URL", "/static/uploads/")

    if database_url == "sqlite:///agrosmart.db":
        app.logger.warning("DATABASE_URL not set; falling back to local SQLite for development.")
