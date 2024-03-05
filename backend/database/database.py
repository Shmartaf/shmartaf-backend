import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()
# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
SQLALCHEMY_DATABASE_URL = (
    f'postgresql://{os.getenv("PGUSER")}:{os.getenv("PGPASSWORD")}@{os.getenv("PGHOST")}:5432/{os.getenv("PGDATABASE")}'
)
# SQLALCHEMY_DATABASE_URL = f'postgresql://postgres.dstkujmlmzynreehsvls:{os.getenv("PGPASSWORD")}@aws-0-eu-central-1.pooler.supabase.com:5432/postgres'


class Database:
    def __init__(self):
        self.engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            pool_size=15,
            max_overflow=20,
        )
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
        )
        self.Base = declarative_base()

    def get_db(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
