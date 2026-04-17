from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool, QueuePool
from app.config import settings

# Configure connection pool based on database type
if "postgresql" in settings.DATABASE_URL:
    # For PostgreSQL: use QueuePool with proper settings
    engine = create_engine(
        settings.DATABASE_URL,
        poolclass=QueuePool,
        pool_size=10,           # Number of connections to keep in pool
        max_overflow=20,        # Maximum overflow connections
        pool_recycle=3600,      # Recycle connections after 1 hour
        pool_pre_ping=True,     # Test connections before using them
        echo=settings.SQLALCHEMY_ECHO
    )
    
    # Add event listener to handle disconnection errors
    @event.listens_for(engine, "connect")
    def receive_connect(dbapi_conn, connection_record):
        dbapi_conn.set_isolation_level(0)
        
else:
    # For SQLite: use simple settings
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=settings.SQLALCHEMY_ECHO
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
