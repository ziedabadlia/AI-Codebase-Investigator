from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# Setup database engine
# Note: For Supabase or poolers, we can customize parameters if needed.
engine = create_engine(
    settings.DATABASE_URL,
    # pool_pre_ping is useful to prevent broken connections
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    FastAPI dependency that yields a database session and closes it after the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
