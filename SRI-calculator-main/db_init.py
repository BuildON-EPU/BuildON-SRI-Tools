from sqlmodel import SQLModel, create_engine
from models import Domain_W, Impact_W, Levels, Services, Building, person
import os

#DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:admin!@db:5432/buildon_sri_db")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:admin!@buildon.epu.ntua.gr:5553/buildon_sri_db")

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)

# Create the database tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

