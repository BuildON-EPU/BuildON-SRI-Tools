from typing import List, Optional, Dict
from sqlmodel import SQLModel, create_engine, Session, select, text
import pandas as pd
from sqlmodel import Field, Relationship, Column, ARRAY, String, JSON, create_engine
from passlib.context import CryptContext
from contextlib import contextmanager

csv_file_path1 = 'Classes_CSV/domain_w.csv'
csv_file_path2 = 'Classes_CSV/impact_w.csv'
csv_file_path3 = 'Classes_CSV/levels_new.csv'
csv_file_path4 = 'Classes_CSV/services.csv'

DATABASE_URL = "postgresql://admin:admin!@db:5432/buildon_sri_db"
engine = create_engine(DATABASE_URL, echo=True)

# Password hashing utility with argon2
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

from sqlalchemy import Column, String

class person(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(sa_column=Column(String, unique=True))
    email: str = Field(sa_column=Column(String, unique=True))
    hashed_password: str
    is_active: bool = Field(default=True)
    buildings: List["Building"] = Relationship(back_populates="owner")



#Define the Domain Weights
class Domain_W(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)  # Primary key
    building_type: str
    zone: str
    domain: str
    dw_cr1: float
    dw_cr2: float
    dw_cr3: float
    dw_cr4: float
    dw_cr5: float
    dw_cr6: float
    dw_cr7: float


#Define the impact weights
class Impact_W(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)  # Primary key
    building_type: str
    zone: str
    imp_cr1: float
    imp_cr2: float
    imp_cr3: float
    imp_cr4: float
    imp_cr5: float
    imp_cr6: float
    imp_cr7: float

#Define the levels
class Levels(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)  # Primary key
    code: str
    level_desc: str
    description: str
    score_cr1: int
    score_cr2: int
    score_cr3: int
    score_cr4: int
    score_cr5: int
    score_cr6: int
    score_cr7: int
    level:int
    mandatory:bool
    domain:str

class Services(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)  # Primary key
    domain:str
    code:str
    service_group:str
    service_desc:str

# Define the Building model
class Building(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    building_name: str
    building_type: str
    building_usage: str
    building_state: str
    energy_class: str
    zone: str
    country: str
    city: str
    region: str
    street: str
    zip: str
    domains: Optional[List[str]] = Field(sa_column=Column(ARRAY(String)))  
    owner_id: Optional[int] = Field(default=None, foreign_key="person.id")
    owner: Optional[person] = Relationship(back_populates="buildings")
    sri_scores: Optional[Dict[str, float]] = Field(sa_column=Column(JSON), default={})  
    total_sri: Optional[float] = 0.0  
    levels: Optional[Dict[str, Dict[int, int]]] = Field(sa_column=Column(JSON), default={}) 
    year_built: str
    

@contextmanager
def get_session():
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()

def truncate_tables():
    with get_session() as session:
        session.execute(text("TRUNCATE TABLE domain_w, impact_w, levels, services RESTART IDENTITY CASCADE;"))
        session.commit()

def load_data_from_csv():
    data1 = pd.read_csv(csv_file_path1, delimiter=',')
    if data1 is None or data1.empty:
        raise ValueError("Data not loaded correctly")
    data2 = pd.read_csv(csv_file_path2, delimiter=',')
    if data2 is None or data2.empty:
        raise ValueError("Data not loaded correctly")
    data3 = pd.read_csv(csv_file_path3, delimiter=';')
    if data3 is None or data3.empty:
        raise ValueError("Data not loaded correctly")
    data4 = pd.read_csv(csv_file_path4, delimiter=',')
    if data4 is None or data4.empty:
        raise ValueError("Data not loaded correctly")

    # Replace NaN values with a default or valid value
    data3['mandatory'] = data3['mandatory'].fillna(False).astype(bool)
    data3['description'] = data3['description'].fillna("Unknown").astype(str)

    # Validate all expected numerical fields
    numerical_fields = ['score_cr1', 'score_cr2', 'score_cr3', 'score_cr4', 'score_cr5', 'score_cr6', 'score_cr7']
    for field in numerical_fields:
        data3[field] = pd.to_numeric(data3[field], errors='coerce').fillna(0)

    with get_session() as session:
        if not session.exec(select(Domain_W)).all():
            for _, row in data1.iterrows():
                domain_w = Domain_W(
                    building_type=row['building_type'],
                    zone=row['zone'],
                    domain=row['domain'],
                    dw_cr1=row['dw_cr1'],
                    dw_cr2=row['dw_cr2'],
                    dw_cr3=row['dw_cr3'],
                    dw_cr4=row['dw_cr4'],
                    dw_cr5=row['dw_cr5'],
                    dw_cr6=row['dw_cr6'],
                    dw_cr7=row['dw_cr7'],
                )
                session.add(domain_w)
        if not session.exec(select(Impact_W)).all():    
            for _, row in data2.iterrows():
                impact_w = Impact_W(
                    building_type=row['building_type'],
                    zone=row['zone'],
                    imp_cr1=row['imp_cr1'],
                    imp_cr2=row['imp_cr2'],
                    imp_cr3=row['imp_cr3'],
                    imp_cr4=row['imp_cr4'],
                    imp_cr5=row['imp_cr5'],
                    imp_cr6=row['imp_cr6'],
                    imp_cr7=row['imp_cr7'],
                )
                session.add(impact_w)
        if not session.exec(select(Levels)).all():    
            for _, row in data3.iterrows():
                # Check for NaN values in critical fields
                if pd.isna(row['description']):
                    raise ValueError("Invalid description found")
                if not isinstance(row['mandatory'], bool):
                    raise ValueError("Mandatory field should be a boolean")
                levels = Levels(
                    code=row['code'],
                    level_desc=row['level_desc'],
                    description=row['description'],
                    score_cr1=row['score_cr1'],
                    score_cr2=row['score_cr2'],
                    score_cr3=row['score_cr3'],
                    score_cr4=row['score_cr4'],
                    score_cr5=row['score_cr5'],
                    score_cr6=row['score_cr6'],
                    score_cr7=row['score_cr7'],
                    level=row['level'],
                    mandatory=row['mandatory'],
                    domain=row['domain']
                )
                session.add(levels)
        if not session.exec(select(Services)).all():    
            for _, row in data4.iterrows():
                services = Services(
                    domain=row['Domain'],
                    code=row['Code'],
                    service_group=row['service_group'],
                    service_desc=row['service_desc']
                )
                session.add(services)
        
        session.commit()




# Create the database tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Function to reset and load data
def reset_and_load_data():
    truncate_tables()
    load_data_from_csv()
