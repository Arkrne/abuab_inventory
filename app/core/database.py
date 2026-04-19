from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# For development, we use SQLite. 
# Because we are using SQLAlchemy, we can swap this exact code to PostgreSQL later with zero structural changes!
SQLALCHEMY_DATABASE_URL = "sqlite:///./abuab_inventory.db"

# The engine is the core connection to the database
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# The session is what we use to talk to the database (add, delete, edit)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# The Base is the blueprint standard all our tables will inherit from
Base = declarative_base()

# Dependency to get a database session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()