from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.core.config import settings # Import settings

engine = None
SessionLocal = None
IS_DB_CONNECTED = False

if settings.SQLALCHEMY_DATABASE_URL:
    try:
        engine = create_engine(
            settings.SQLALCHEMY_DATABASE_URL,
            # pool_pre_ping=True # Good practice for checking connections
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        print("Database engine and session created successfully.")
        IS_DB_CONNECTED = True # Assume connection is possible if URL is valid

    except Exception as e:
        print(f"CRITICAL: Error creating database engine or session: {e}")
        print("Database operations will fail.")
        engine = None
        SessionLocal = None
else:
    print("Database URL not configured, skipping engine creation.")

Base = declarative_base()

# --- Dependency for FastAPI ---
def get_db():
    """FastAPI dependency to get a DB session."""
    if not SessionLocal:
        yield None # Indicate DB is not available
        return

    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()