from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, constr
from typing import Dict, List, Optional
from sqlmodel import Session, select
from sqlalchemy.exc import SQLAlchemyError
from models import get_session, Levels, Domain_W, Impact_W, Services, Building, person, pwd_context, create_db_and_tables, reset_and_load_data
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
import logging
import json
import os
from sqlmodel import Session
from db_init import create_db_and_tables
import requests


# Initialize the FastAPI application
app = FastAPI(debug=True)
api_router = APIRouter(prefix="/api")

# # Call create_db_and_tables globally
# create_db_and_tables()

@app.on_event("startup")
async def startup_event():
    create_db_and_tables()

# Configure CORS
origins = [
    "https://sri.buildon.epu.ntua.gr",  # React frontend on the server
    "http://sri.buildon.epu.ntua.gr",  # React frontend on the server
    "http://buildon.epu.ntua.gr:3003",  # React frontend on the server
    "http://localhost:3003",  # React frontend
    "http://localhost:3000",  # React frontend
    "http://127.0.0.1:3000",  # Another possible localhost address
]

# Secret key for JWT token
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    #allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# if __name__ == "__main__":
#     create_db_and_tables()

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

create_db_and_tables()


# Define a Pydantic model for the Building input
class BuildingInput(BaseModel):
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
    domains: Optional[List[str]] = []  # Make domains optional and default to empty list
    year_built: str

    class Config:
        orm_mode = True

class BuildingOutput(BaseModel):
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
    domains: List[str]  # Add this line
    owner_id: int
    levels: Dict[str, Dict[int, int]]
    year_built: str

    class Config:
        orm_mode = True

class UpdateBuildingDomains(BaseModel):
    domains: List[str]


# Define a Pydantic model for the SRI calculation input
class SRIInput(BaseModel):
    building_type: str
    zone: str
    dom: List[str] #list with the present domains
    lev: Dict[str, Dict[int, int]]  # Dictionary with service.code as key and another dictionary as value


# Define a Pydantic model for the SRI output
class SRIOutput(BaseModel):
    #domain_impact_scores: Dict[str, int]  # Domain-impact criteria scores (not necessary)
    #domain_max_scores: Dict[str, int] #not necessary
    smart_readiness_scores: Dict[str, float]  # The new percentage score, allowing float
    #weighted_impact_sums: Dict[str, float]  # Weighted sums for each impact criterion (not necessary)
    #weighted_max_sums: Dict[str, float]  # Weighted sums for each impact criterion using lmax(d, ic) (not necessary)
    sr_impact_criteria: Dict[str, float]  # New percentage score for each impact criterion
    sr_domains: Dict[str, float]  # Smart Readiness score for each domain
    srf_scores: Dict[str, float] # Percentage for the SRf score for 3 key functionalities
    total_sri: float  # New field for the total SRI score


# Validate data before inserting into the database
def validate_numeric_data(data):
    for key, value in data.items():
        # Check if the value is supposed to be a double precision
        if key.startswith("score_"):
            try:
                float(value)  # Ensure the value can be converted to float
            except ValueError:
                raise ValueError(f"Invalid numeric value for {key}: {value}")
            

def calculate_scores(user_input: SRIInput):
    with get_session() as session:
        domain_impact_scores = {}
        domain_max_scores = {}  # To store Imax(d, ic)
        smart_readiness_scores = {} #to store SR(d, ic) percentage

        #domains = [ "Cooling", "Dynamic building envelope", "Domestic hot water", "Electricity", "Electric vehicle charging", "Heating", "Lighting", "Monitoring and control", "Ventilation"]

        domains = user_input.dom

        # Mandatory services mapping as per domain
        mandatoryServices = {
            'Heating': ['H-3', 'H-4'],
            'Domestic hot water': ['DHW-3'],
            'Cooling': ['C-1f', 'C-2a', 'C-3', 'C-4'],
            'Ventilation': ['V-1a', 'V-6'],
            'Lighting': ['L-1a', 'L-2'],
            'Dynamic building envelope': ['DE-2'],
            'Electricity': ['E-12'],
            'Monitoring and control': ['MC-3', 'MC-4', 'MC-9', 'MC-13', 'MC-25', 'MC-28', 'MC-29', 'MC-30'],
        }

        impact_criteria = [
            "Energy efficiency", "Energy, flexibility and storage", "Comfort", "Convenience", "Health, wellbeing and accessibility", 
            "Maintenance and fault prediction", "Information to occupants"
        ]

        # Loop over domains and impact criteria
        for domain in domains:
            # Initialize a dictionary to store the maximum scores for each impact criterion
            max_scores = {ic: 0 for ic in impact_criteria}

            # Get all levels in the current domain
            domain_levels = session.query(Levels).filter(Levels.domain == domain).all()

            # Create a dictionary to store the maximum level for each service code
            max_level_for_service = {}

            for level in domain_levels:
                # Determine the maximum level for each service code
                if level.code in user_input.lev:
                    if level.code not in max_level_for_service or max_level_for_service[level.code] < level.level:
                        max_level_for_service[level.code] = level.level
            # Include mandatory services for the current domain
            mandatory_services = mandatoryServices.get(domain, [])

            for mandatory_service in mandatory_services:
                # Get all levels for the mandatory service
                mandatory_service_levels = session.query(Levels).filter(Levels.code == mandatory_service).all()
                for level in mandatory_service_levels:
                    if mandatory_service not in max_level_for_service or max_level_for_service[mandatory_service] < level.level:
                        max_level_for_service[mandatory_service] = level.level            
            #score_fields = [ "score_cr1", "score_cr2", "score_cr3", "score_cr4", "score_cr5", "score_cr6", "score_cr7"]

            # Calculate the maximum score for each impact criterion
            for ic in impact_criteria:

                if ic == "Energy efficiency":
                    score_field = "score_cr1"
                if ic == "Energy, flexibility and storage":
                    score_field = "score_cr2"
                if ic == "Comfort":
                    score_field = "score_cr3"
                if ic == "Convenience":
                    score_field = "score_cr4"
                if ic == "Health, wellbeing and accessibility":
                    score_field = "score_cr5"
                if ic == "Maintenance and fault prediction":
                    score_field = "score_cr6"
                if ic == "Information to occupants":
                    score_field = "score_cr7"

                for service_code, max_level in max_level_for_service.items():
                    # Find the level instance with the maximum level for this service
                    max_level_instance = session.query(Levels).filter(
                        Levels.code == service_code,
                        Levels.level == max_level
                    ).first()

                    if max_level_instance:
                        score = getattr(max_level_instance, score_field, 0)
                        max_scores[ic] += score

                # Store the calculated Imax(d, ic)
                domain_max_scores[f"{domain}-{ic}"] = max_scores[ic]

            # Now calculate the l(d, ic) score as before
            for ic in impact_criteria:
                total_score = 0

                # Calculate the score based on the user's input
                for level in domain_levels:
                    level_input = user_input.lev.get(level.code)  # Get the user input level
                    if level_input:  # Match the user input with the level


                        # Get the score for the corresponding impact criteria
                        if ic == "Energy efficiency":
                            score_field = "score_cr1"
                        if ic == "Energy, flexibility and storage":
                            score_field = "score_cr2"
                        if ic == "Comfort":
                            score_field = "score_cr3"
                        if ic == "Convenience":
                            score_field = "score_cr4"
                        if ic == "Health, wellbeing and accessibility":
                            score_field = "score_cr5"
                        if ic == "Maintenance and fault prediction":
                            score_field = "score_cr6"
                        if ic == "Information to occupants":
                            score_field = "score_cr7"

                        level_scores = []
                        for user_level, percentage in level_input.items():
                            if level.level == user_level:
                                score = getattr(level, score_field, 0) * (percentage / 100)
                                level_scores.append(score)
                        total_score += sum(level_scores)

                domain_impact_scores[f"{domain}-{ic}"] = total_score
        
        # Calculate SR(d, ic) as (l(d, ic) / lmax(d, ic)) * 100
        for key in domain_impact_scores:
            l_score = domain_impact_scores[key]
            lmax_score = domain_max_scores[key]
            if lmax_score != 0:  # Avoid division by zero
                smart_readiness_score = (l_score / lmax_score) * 100
            else:
                smart_readiness_score = 0  # If lmax_score is zero, SR is 0

            smart_readiness_scores[key] = round(smart_readiness_score, 2)  # Round to two decimal places


    return {
            "domain_impact_scores": domain_impact_scores,
            "domain_max_scores": domain_max_scores,
            "smart_readiness_scores": smart_readiness_scores,
        }


# Function to calculate the weighted sums for each impact criterion
def calculate_weighted_sums(user_input: SRIInput, impact_scores: Dict[str, int]):
    with get_session() as session:
        

        impact_criteria = [
            "Energy efficiency", "Energy, flexibility and storage", "Comfort", "Convenience", "Health, wellbeing and accessibility", 
            "Maintenance and fault prediction", "Information to occupants"
        ]

        # Initialize the weighted sums dictionary
        weighted_sums = {ic: 0 for ic in impact_criteria}

        # Loop through the domain-impact scores and calculate the weighted sums
        for key, score in impact_scores.items():
            try:
                domain, impact_criterion = key.split("-")  # Split the key into domain and impact criterion
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid key structure: '{key}'. Expected format 'Domain-ImpactCriterion'"
                )
            
                # Get the correct weights based on the building type and zone
            domain_weights = session.query(Domain_W).filter(
                Domain_W.building_type == user_input.building_type,
                Domain_W.zone == user_input.zone,
                Domain_W.domain == domain
            ).first()

            if not domain_weights:
                raise HTTPException(status_code=400, detail="No weights found for the given zone and building type")

            # Ensure the impact_criterion is valid
            if impact_criterion not in impact_criteria:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unknown impact criterion: '{impact_criterion}'."
                )

            # Get the correct weight for the given impact criterion
            if impact_criterion == "Energy efficiency":
                    weight_field = "dw_cr1"
            if impact_criterion == "Energy, flexibility and storage":
                    weight_field = "dw_cr2"
            if impact_criterion == "Comfort":
                    weight_field = "dw_cr3"
            if impact_criterion == "Convenience":
                    weight_field = "dw_cr4"
            if impact_criterion == "Health, wellbeing and accessibility":
                    weight_field = "dw_cr5"
            if impact_criterion == "Maintenance and fault prediction":
                    weight_field = "dw_cr6"
            if impact_criterion == "Information to occupants":
                    weight_field = "dw_cr7"
            #weight_index = impact_criteria.index(impact_criterion) + 1  # dw_cr1, dw_cr2, etc.
            weight = getattr(domain_weights, weight_field, 1)
            weighted_sums[impact_criterion] += weight * score

        return weighted_sums


# Adding fixed weights for the impact criteria
impact_weights = {
    "Energy efficiency": 0.5,
    "Energy, flexibility and storage": 1,
    "Comfort": 0.25,
    "Convenience": 0.25,
    "Health, wellbeing and accessibility": 0.25,
    "Maintenance and fault prediction": 0.5,
    "Information to occupants": 0.25
}

# Define the key functionalities and their associated impact criteria
key_functionalities = {
    "Energy Performance and Operation": ["Energy efficiency", "Maintenance and fault prediction"],
    "Response to User Needs": ["Comfort", "Convenience", "Information to occupants", "Health, wellbeing and accessibility"],
    "Energy Flexibility": ["Energy, flexibility and storage"]
}

# Function to calculate weighted domain sums
def calculate_weighted_domain_sums(domain_impact_scores):
    weighted_domain_sums = {}  # Initialize the weighted sums for each domain
    
    # Loop through the domain-impact scores
    for key, score in domain_impact_scores.items():
        domain, impact_criterion = key.split("-")
        
        if domain not in weighted_domain_sums:
            weighted_domain_sums[domain] = 0
        
        # Add weighted score to the domain's total
        weighted_domain_sums[domain] += impact_weights[impact_criterion] * score

    return weighted_domain_sums


# Function to calculate SR for each domain
def calculate_sr_domains(weighted_domain_sums, weighted_max_domain_sums):
    sr_domains = {}  # Initialize SR for each domain
    
    for domain in weighted_domain_sums:
        domain_sum = weighted_domain_sums[domain]
        max_domain_sum = weighted_max_domain_sums.get(domain, 0)
        
        if max_domain_sum != 0:
            sr_domain = (domain_sum / max_domain_sum) * 100  # Calculate SR(d)
        else:
            sr_domain = 0
        
        sr_domains[domain] = round(sr_domain, 2)  # Round to two decimal places

    return sr_domains


# Function to calculate SRf scores for each key functionality
def calculate_srf_scores(sr_impact_criteria):
    srf_scores = {}  # Initialize the SRf scores dictionary
    
    # Calculate the weighted SRf score for each key functionality
    for key_func, impact_criteria in key_functionalities.items():
        srf_score = 0
        
        # Sum the weighted SR(ic) for each impact criterion within the key functionality
        for impact_criterion in impact_criteria:
            if impact_criterion in sr_impact_criteria:  # Corrected key reference
                srf_score += impact_weights[impact_criterion] * sr_impact_criteria[impact_criterion]
        
        # Convert to percentage and round to two decimal places
        srf_scores[key_func] = round(srf_score, 2)

    return srf_scores


# Function to calculate the total SRI score
def calculate_total_sri(srf_scores: Dict[str, float]):
    # Weights for each key functionality
    weight = 1 / 3  # Equal weight for each key functionality
    
    total_sri = 0

    # Sum weighted SRf scores
    for key in srf_scores:
        total_sri += srf_scores[key] * weight
    
    return round(total_sri, 2)  # Round to two decimal places


# Dependency to get the current user
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    with get_session() as session:
        user = session.query(person).filter(person.username == token_data.username).first()
        if user is None:
            raise credentials_exception
    return user

# Endpoint to add a new building
@api_router.post("/add_building/")
def add_building(input_data: BuildingInput, request: Request, response: Response, current_user: person = Depends(get_current_user)):
    try:
        with get_session() as session:
            building = Building(
                building_name = input_data.building_name,
                building_type=input_data.building_type,
                zone=input_data.zone,
                country=input_data.country,
                city=input_data.city,
                year_built=input_data.year_built,
                #domains=input_data.domains,  # Add domains to the building creation
                owner_id=current_user.id,
                building_usage = input_data.building_usage,
                building_state = input_data.building_state,
                energy_class = input_data.energy_class,
                region = input_data.region,
                street = input_data.street,
                zip = input_data.zip
            )
            session.add(building)
            session.commit()
            session.refresh(building)  # Ensure the building object is refreshed to get the ID
            response.set_cookie(key="current_building", value=building.building_name)
            return building
            #return {"message": "Building added successfully", "building": building}
    except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
            session.rollback()
            logging.error(f"An unexpected error occurred: {str(e)}")
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

# Get current building endpoint
@api_router.get("/current_building/", response_model=BuildingOutput)
def get_current_building(request: Request, current_user: person = Depends(get_current_user)):
    current_building_name = request.cookies.get("current_building")
    if not current_building_name:
        raise HTTPException(status_code=404, detail="No current building set")
    
    with get_session() as session:
        building = session.query(Building).filter(Building.building_name == current_building_name, Building.owner_id == current_user.id).first()
        if not building:
            raise HTTPException(status_code=404, detail="Building not found")
    
    return building


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str, session: Session):
    user = session.query(person).filter(person.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

# Sign-up endpoint
@api_router.post("/signup/")
async def sign_up(user: UserCreate):
    with get_session() as session:
        try:
            print(f"Received signup request: {user}")
            hashed_password = get_password_hash(user.password)
            db_user = person(username=user.username, email=user.email, hashed_password=hashed_password)
            session.add(db_user)
            session.commit()
            return {"message": "User created successfully"}
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Database error: {e}")
            raise HTTPException(status_code=400, detail="Username or email already exists")
        except Exception as e:
            session.rollback()
            print(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred")

# Token endpoint
@api_router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    with get_session() as session:
        user = authenticate_user(form_data.username, form_data.password, session)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}


# Example protected route
@api_router.get("/users/me/")
async def read_users_me(current_user: person = Depends(get_current_user)):
    return current_user

@api_router.get("/users/{username}")
async def read_user(username: str):
    with get_session() as session:
        user = session.query(person).filter(person.username == username).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user

@api_router.get("/profile/", response_model=person)
def read_profile(current_user: person = Depends(get_current_user)):
    return current_user

# Endpoint to retrieve buildings for the logged-in user
@api_router.get("/my_buildings/")
def get_user_buildings(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    with get_session() as session:
        user = session.query(person).filter(person.username == username).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        buildings = session.query(Building).filter(Building.owner_id == user.id).all()
        return buildings

@api_router.get("/services/{domain_name}")
def get_services(domain_name: str):
    with get_session() as session:
        statement = select(Services).distinct(Services.code, Services.service_desc).where(
            Services.domain == domain_name,
            ~Services.service_desc.like('User defined smart ready service%'))
        results = session.exec(statement).all()
        return JSONResponse(content=[result.dict() for result in results])

@api_router.get("/levels/{service_code}")
def get_levels(service_code: str):
    with get_session() as session:
        statement = select(Levels).distinct(Levels.level_desc, Levels.description, Levels.code, Levels.level).where(Levels.code == service_code)
        results = session.exec(statement).all()
        return JSONResponse(content=[result.dict() for result in results])


@api_router.post("/save_sri_levels/")
def save_sri_levels(sri_levels: SRIInput):    
    with get_session() as session:
        # Create the JSON structure
        sri_json = {
            "building_type": sri_levels.building_type,
            "zone": sri_levels.zone,
            "lev": sri_levels.lev
        }
    return JSONResponse(sri_json)
    #return {"message": "SRI levels saved successfully", "sri_json": sri_json}
    

@api_router.post("/calculate-sri/{building_id}/", response_model=SRIOutput)
def calculate_sri(building_id: int, user_input: SRIInput):

    try:
        validate_numeric_data(user_input.lev)  # Validate numeric fields
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    try:
        # Calculate the domain-impact criteria scores and additional metrics
        calculated_scores = calculate_scores(user_input)
        
        # Ensure returned value is a dictionary
        if not isinstance(calculated_scores, dict):
            raise HTTPException(status_code=500, detail="Unexpected return value from calculate_scores()")

        domain_impact_scores = calculated_scores.get("domain_impact_scores", {})
        domain_max_scores = calculated_scores.get("domain_max_scores", {})
        smart_readiness_scores = calculated_scores.get("smart_readiness_scores", {})

        # Calculate the weighted sums for each impact criterion
        weighted_sums = calculate_weighted_sums(user_input, domain_impact_scores)
        weighted_max_sums = calculate_weighted_sums(user_input, domain_max_scores)
        
        sr_impact_criteria = {}  # New dictionary for SR(ic) percentages

        # Calculate SR(ic) as (weighted_sums[ic] / weighted_max_sums[ic]) * 100
        for ic in weighted_sums:
            weighted_sum = weighted_sums[ic]
            weighted_max_sum = weighted_max_sums[ic]

            if weighted_max_sum != 0:
                sr_percentage = (weighted_sum / weighted_max_sum) * 100
            else:
                sr_percentage = 0  # Default to zero if division by zero risk

            sr_impact_criteria[ic] = round(sr_percentage, 2)  # Round to two decimal places

        # Calculate SRf scores for each key functionality
        srf_scores = calculate_srf_scores(sr_impact_criteria)

        # Calculate the total SRI score
        total_sri = calculate_total_sri(srf_scores)

        # Calculate the weighted sums for each domain
        weighted_domain_sums = calculate_weighted_domain_sums(domain_impact_scores)
        weighted_max_domain_sums = calculate_weighted_domain_sums(domain_max_scores)
        
        # Calculate SR(d) for each domain
        sr_domains = calculate_sr_domains(weighted_domain_sums, weighted_max_domain_sums)


    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

    # Return all expected results
    sri_result = {
        #"domain_impact_scores": domain_impact_scores,
        #"domain_max_scores": domain_max_scores,
        "smart_readiness_scores": smart_readiness_scores,
        #"weighted_impact_sums": weighted_sums,
        #"weighted_max_sums": weighted_max_sums,
        "sr_impact_criteria": sr_impact_criteria,  
        "sr_domains": sr_domains,
        "srf_scores": srf_scores,
        "total_sri": total_sri
    }

    # # Save the results as a JSON file
    # try:
    #     output_path = os.path.join('/Users/giannispapias/Desktop/Server/SRI-calculator/', f"sri_output_{building_id}.json")
    #     with open(output_path, "w") as json_file:
    #         json.dump(sri_result, json_file, indent=4)
    #     print(f"SRI output saved to {output_path}")
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"Failed to save SRI output as JSON: {str(e)}")
    
    # Save the results to the building
    with get_session() as session:
        building = session.get(Building, building_id)
        if building:
            building.sri_scores = sri_result
            building.total_sri = total_sri
            building.levels = user_input.lev
            session.add(building)
            session.commit()
    
    return sri_result

@api_router.put("/buildings/{building_id}/domains", response_model=BuildingOutput)
def update_building_domains(building_id: int, response: Response, domains_data: UpdateBuildingDomains):
    with get_session() as session:
        statement = select(Building).where(Building.id == building_id)
        results = session.exec(statement)
        building = results.one_or_none()

        if not building:
            raise HTTPException(status_code=404, detail="Building not found")

        building.domains = domains_data.domains
        session.add(building)
        session.commit()
        session.refresh(building)

    return building

@api_router.get("/building/{building_id}/sri_scores/", response_model=SRIOutput)
def get_sri_scores(building_id: int):
    with get_session() as session:
        building = session.get(Building, building_id)
        if not building or not building.sri_scores:
            raise HTTPException(status_code=404, detail="SRI scores not found for this building")
        
        return building.sri_scores

   
@api_router.get("/building/{building_id}/", response_model=BuildingOutput)
def get_curr_building(building_id: int, response: Response):
    with get_session() as session:
        statement = select(Building).where(Building.id == building_id)
        building = session.exec(statement).first()
        if not building:
            raise HTTPException(status_code=404, detail="Building not found")
    print(building)
    return building

def calculate_sri_help(building_id: int, user_input: SRIInput):

    try:
        validate_numeric_data(user_input.lev)  # Validate numeric fields
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    try:
        # Calculate the domain-impact criteria scores and additional metrics
        calculated_scores = calculate_scores(user_input)
        
        # Ensure returned value is a dictionary
        if not isinstance(calculated_scores, dict):
            raise HTTPException(status_code=500, detail="Unexpected return value from calculate_scores()")

        domain_impact_scores = calculated_scores.get("domain_impact_scores", {})
        domain_max_scores = calculated_scores.get("domain_max_scores", {})
        smart_readiness_scores = calculated_scores.get("smart_readiness_scores", {})

        # Calculate the weighted sums for each impact criterion
        weighted_sums = calculate_weighted_sums(user_input, domain_impact_scores)
        weighted_max_sums = calculate_weighted_sums(user_input, domain_max_scores)
        
        sr_impact_criteria = {}  # New dictionary for SR(ic) percentages

        # Calculate SR(ic) as (weighted_sums[ic] / weighted_max_sums[ic]) * 100
        for ic in weighted_sums:
            weighted_sum = weighted_sums[ic]
            weighted_max_sum = weighted_max_sums[ic]

            if weighted_max_sum != 0:
                sr_percentage = (weighted_sum / weighted_max_sum) * 100
            else:
                sr_percentage = 0  # Default to zero if division by zero risk

            sr_impact_criteria[ic] = round(sr_percentage, 2)  # Round to two decimal places

        # Calculate SRf scores for each key functionality
        srf_scores = calculate_srf_scores(sr_impact_criteria)

        # Calculate the total SRI score
        total_sri = calculate_total_sri(srf_scores)

        # Calculate the weighted sums for each domain
        #weighted_domain_sums = calculate_weighted_domain_sums(domain_impact_scores)
        #weighted_max_domain_sums = calculate_weighted_domain_sums(domain_max_scores)
        
        # Calculate SR(d) for each domain
        #sr_domains = calculate_sr_domains(weighted_domain_sums, weighted_max_domain_sums)


    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

    # Return all expected results
    sri_result = {
        "smart_readiness_scores": smart_readiness_scores,
        "sr_impact_criteria": sr_impact_criteria,  
        "srf_scores": srf_scores,
        "total_sri": total_sri
    }
    
    return sri_result


class SRIUpgradeRequest(BaseModel):
    target_sri: float

def get_next_level(service_code: str, current_level: int, session: Session) -> Optional[int]:
    next_level = session.query(Levels).filter_by(code=service_code, level=current_level + 1).first()
    return next_level.level if next_level else None

def apply_level_change(service_code: str, new_level: int, levels: dict) -> dict:
    new_levels = {k: v.copy() for k, v in levels.items()}
    if service_code in new_levels:
        new_levels[service_code] = {new_level: 100}
    return new_levels

def explore_configurations(session: Session, current_config: dict, target_sri: float, 
                           all_possible_upgrades: list, building_id: int) -> None:
    
    building = session.get(Building, building_id)
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    
    for service_code, levels in current_config.items():
        current_level = max(levels.keys(), key=int)
        next_level = get_next_level(service_code, int(current_level), session)
        
        if next_level is None:
            continue  # Skip if there's no higher level
        
        # Apply the change
        new_config = apply_level_change(service_code, next_level, current_config)
        
        # Recalculate SRI
        new_input = SRIInput(building_type=building.building_type,
                             zone=building.zone, dom=building.domains, lev=new_config)
        sri_scores = calculate_sri_help(building_id, new_input)
        total_sri = sri_scores.get("total_sri", 0)
        
        if total_sri >= target_sri:
            all_possible_upgrades.append({
                "config": new_config,
                "achieved_sri": total_sri
            })
        # Explore further changes
        elif total_sri < target_sri:
            explore_configurations(session, new_config, target_sri, all_possible_upgrades, building_id)
            break
            
        
def calculate_individual_sri_increase(service_code, original_level, upgraded_levels, original_sri, building, session):
    """
    Calculate the individual SRI increase for a specific service upgrade.
    """
    # Revert the service to its original level
    temp_config = upgraded_levels.copy()
    temp_config[service_code] = {original_level: 100}

    # Recalculate SRI for the configuration with only this service not upgraded
    new_input = SRIInput(building_type=building.building_type,
                         zone=building.zone, dom=building.domains, lev=temp_config)
    sri_scores = calculate_sri_help(building.id, new_input)
    sri_with_reverted_service = sri_scores.get("total_sri", 0)

    # The contribution is the difference
    return round(original_sri - sri_with_reverted_service, 2)

# ----- Changed to not use the written json ---------
# @api_router.post("/upgrade_sri/{building_id}/")
# def upgrade_sri(building_id: int, request: SRIUpgradeRequest):
#     with get_session() as session:
#         target_sri = request.target_sri
#         building = session.get(Building, building_id)
#         if not building:
#             raise HTTPException(status_code=404, detail="Building not found")

#         current_sri = building.total_sri
#         if target_sri <= current_sri:
#             raise HTTPException(status_code=400, detail="Target SRI must be greater than the current SRI.")

#         user_input = {
#             "building_type": building.building_type,
#             "zone": building.zone,
#             "dom": building.domains,
#             "lev": building.levels  # Assuming this is stored with the building
#         }

#         all_possible_upgrades = []

#         # Start exploration from the current configuration
#         explore_configurations(session, user_input['lev'], target_sri, all_possible_upgrades, building_id)

#         if not all_possible_upgrades:
#             return {"message": "No valid upgrades found"}

#         # Sort and return the best upgrade (minimal score above target)
#         best_upgrade = min(all_possible_upgrades, key=lambda x: x['achieved_sri'])

#         original_levels = user_input['lev']
#         upgrades = best_upgrade['config']
#         new_sri = best_upgrade['achieved_sri']

#         # Calculate the individual increases
#         individual_increases = {}
#         filtered_upgrades = {}
#         filtered_original_levels = {}
#         for service_code, original_level in original_levels.items():
#             original_level_key = max(original_level.keys(), key=int)
#             upgraded_level_key = max(upgrades.get(service_code, {}).keys(), key=int)

#             if original_level_key != upgraded_level_key:
#                 individual_increase = calculate_individual_sri_increase(
#                     service_code, original_level_key, upgrades, new_sri, building, session)
#                 # Only include services where the level changed
#                 filtered_upgrades[service_code] = upgrades[service_code]
#                 filtered_original_levels[service_code] = original_level
#                 individual_increases[service_code] = individual_increase

#             individual_increases[service_code] = individual_increase

#         response = {
#             "Upgrades": filtered_upgrades,  # Send filtered upgrades
#             "New_Score": new_sri,
#             "Original_Levels": filtered_original_levels,  # Send filtered original levels
#             "Individual_Increases": individual_increases  # Only include increases for changed services
#         }

#         return response

@api_router.post("/upgrade_sri/{building_id}/")
def upgrade_sri(building_id: int, request: SRIUpgradeRequest):
    with get_session() as session:
        target_sri = request.target_sri
        building = session.get(Building, building_id)
        if not building:
            raise HTTPException(status_code=404, detail="Building not found")

        current_sri = building.total_sri
        if target_sri <= current_sri:
            raise HTTPException(status_code=400, detail="Target SRI must be greater than the current SRI.")

        # Prepare the user input for processing
        user_input = {
            "building_type": building.building_type,
            "zone": building.zone,
            "dom": building.domains,
            "lev": building.levels  # Assuming this is stored with the building
        }

        all_possible_upgrades = []

        # Start exploration from the current configuration
        explore_configurations(session, user_input['lev'], target_sri, all_possible_upgrades, building_id)

        if not all_possible_upgrades:
            return {"message": "No valid upgrades found"}

        # Sort and return the best upgrade (minimal score above target)
        best_upgrade = min(all_possible_upgrades, key=lambda x: x['achieved_sri'])

        original_levels = user_input['lev']
        upgrades = best_upgrade['config']
        new_sri = best_upgrade['achieved_sri']

        # Calculate the individual increases
        individual_increases = {}
        filtered_upgrades = {}
        filtered_original_levels = {}

        for service_code, original_level in original_levels.items():
            original_level_key = max(original_level.keys(), key=int)
            upgraded_level_key = max(upgrades.get(service_code, {}).keys(), key=int)

            if original_level_key != upgraded_level_key:
                individual_increase = calculate_individual_sri_increase(
                    service_code, original_level_key, upgrades, new_sri, building, session)
                # Only include services where the level changed
                filtered_upgrades[service_code] = upgrades[service_code]
                filtered_original_levels[service_code] = original_level
                individual_increases[service_code] = individual_increase

        # Construct the response data
        response = {
            "Upgrades": filtered_upgrades,  # Filtered upgrades
            "New_Score": new_sri,
            "Original_Levels": filtered_original_levels,  # Original levels for comparison
            "Individual_Increases": individual_increases  # Contributions of each upgrade
        }

        return response


@app.on_event("startup")
async def startup_event():
    reset_and_load_data()

# @api_router.post("/upgrade-scenarios/{building_id}/", response_model=SRIOutput)
# def possible_upgrades(building_id: int, user_input: SRIInput, current_user: person = Depends(get_current_user)):
#     try:
#         validate_numeric_data(user_input.lev)  # Validate numeric fields
#     except ValueError as ve:
#         raise HTTPException(status_code=400, detail=str(ve))
    
#     # Retrieve the building from the database using building_id
#     with get_session() as session:
#         building = session.get(Building, building_id)
        
#         if not building:
#             raise HTTPException(status_code=404, detail="Building not found")
        
#         # Ensure we have the expected building data
#         if not building.levels:
#             raise HTTPException(status_code=400, detail="Building levels data is missing")
    
    
#     try:
#         # Calculate the domain-impact criteria scores and additional metrics
#         calculated_scores = calculate_scores(user_input)
        
#         # Ensure returned value is a dictionary
#         if not isinstance(calculated_scores, dict):
#             raise HTTPException(status_code=500, detail="Unexpected return value from calculate_scores()")

#         domain_impact_scores = calculated_scores.get("domain_impact_scores", {})
#         domain_max_scores = calculated_scores.get("domain_max_scores", {})
#         smart_readiness_scores = calculated_scores.get("smart_readiness_scores", {})

#         # Calculate the weighted sums for each impact criterion
#         weighted_sums = calculate_weighted_sums(user_input, domain_impact_scores)
#         weighted_max_sums = calculate_weighted_sums(user_input, domain_max_scores)
        
#         sr_impact_criteria = {}  # New dictionary for SR(ic) percentages

#         # Calculate SR(ic) as (weighted_sums[ic] / weighted_max_sums[ic]) * 100
#         for ic in weighted_sums:
#             weighted_sum = weighted_sums[ic]
#             weighted_max_sum = weighted_max_sums[ic]

#             if weighted_max_sum != 0:
#                 sr_percentage = (weighted_sum / weighted_max_sum) * 100
#             else:
#                 sr_percentage = 0  # Default to zero if division by zero risk

#             sr_impact_criteria[ic] = round(sr_percentage, 2)  # Round to two decimal places

#         # Calculate SRf scores for each key functionality
#         srf_scores = calculate_srf_scores(sr_impact_criteria)

#         # Calculate the total SRI score
#         total_sri = calculate_total_sri(srf_scores)

#         # Calculate the weighted sums for each domain
#         weighted_domain_sums = calculate_weighted_domain_sums(domain_impact_scores)
#         weighted_max_domain_sums = calculate_weighted_domain_sums(domain_max_scores)
        
#         # Calculate SR(d) for each domain
#         sr_domains = calculate_sr_domains(weighted_domain_sums, weighted_max_domain_sums)

#     except SQLAlchemyError as e:
#         raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

#     # Create the SRI result similar to the calculate_sri function
#     sri_result = {
#         "smart_readiness_scores": smart_readiness_scores,
#         "sr_impact_criteria": sr_impact_criteria,  
#         "sr_domains": sr_domains,
#         "srf_scores": srf_scores,
#         "total_sri": total_sri
#     }

#     # Generate the formatted DST data
#     dst_format = {
#         "user": current_user.id,
#         "input_sri": sri_result["total_sri"],
#         "building_type": user_input.building_type,
#         "zone": user_input.zone,
#         "domain_scores": [{"domain": domain, "percentage": score, "score": sr_domains.get(domain, 0)} for domain, score in sr_domains.items()],
#         "impact_scores": [{"impact": ic, "percentage": score, "score": sr_impact_criteria.get(ic, 0)} for ic, score in sr_impact_criteria.items()],
#         "key_functionalities_scores": [{"key_functionality": kf, "percentage": score} for kf, score in srf_scores.items()],
#         "services": [
#             {"service": "service_name", "service_code": code, "level": max(levels.keys()), "domain": "domain", "functionality": "description"} 
#             for code, levels in user_input.lev.items()
#         ]
#     }

#     print(dst_format)

#     # Save the result to the building
#     with get_session() as session:
#         building = session.get(Building, building_id)
#         if not building:
#             raise HTTPException(status_code=404, detail="Building not found!!!!!")
#         if building:
#             building.sri_scores = sri_result
#             building.total_sri = total_sri
#             building.levels = user_input.lev
#             session.add(building)
#             session.commit()

#     # Return the formatted data for DST
#     return dst_format

class Service(BaseModel):
    service_code: str
    level: int
    percentage: float

class DstFormat(BaseModel):
    user: int
    input_sri: float
    building_type: str
    zone: str
    domain_scores: Dict[str, float]
    impact_scores: Dict[str, float]
    key_functionalities_scores: Dict[str, float]
    services: List[Service]

# Create an in-memory store for dst_formats for simplicity.
dst_format_store = {}    

### old
# @api_router.post("/upgrade-scenarios/{building_id}/", response_model=DstFormat)
# #def possible_upgrades(building_id: int, user_input: SRIInput, current_user: person = Depends(get_current_user)):
# def possible_upgrades(building_id: int, user_input: SRIInput):
    
#     # Log incoming request data
#     print(f"Received user_input: {user_input}")

#     save_path = '/Users/giannispapias/Desktop/Server/SRI-calculator/' # Change this to your desired directory
#     os.makedirs(save_path, exist_ok=True)  # Ensure the directory exists
    
#     # Create the filename and full path
#     filename = f"user_input_endpoint.json"
#     file_path = os.path.join(save_path, filename)
    
#     # Serialize and save the user_input and building_id as a JSON file
#     try:
#         data_to_save = {
#             "user_input": user_input.dict()  # Convert Pydantic model to a dict
#         }
        
#         with open(file_path, "w") as json_file:
#             json.dump(data_to_save, json_file, indent=4)
        
#         print(f"Data saved to {file_path}")
    
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to save user input as JSON: {str(e)}")
    
    
#     try:
#         validate_numeric_data(user_input.lev)  # Validate numeric fields
#     except ValueError as ve:
#         raise HTTPException(status_code=400, detail=str(ve))
    
#     try:
#         # Calculate the domain-impact criteria scores and additional metrics
#         calculated_scores = calculate_scores(user_input)
        
#         # Ensure returned value is a dictionary
#         if not isinstance(calculated_scores, dict):
#             raise HTTPException(status_code=500, detail="Unexpected return value from calculate_scores()")

#         domain_impact_scores = calculated_scores.get("domain_impact_scores", {})
#         domain_max_scores = calculated_scores.get("domain_max_scores", {})
#         smart_readiness_scores = calculated_scores.get("smart_readiness_scores", {})

#         # Calculate the weighted sums for each impact criterion
#         weighted_sums = calculate_weighted_sums(user_input, domain_impact_scores)
#         weighted_max_sums = calculate_weighted_sums(user_input, domain_max_scores)
        
#         sr_impact_criteria = {}  # New dictionary for SR(ic) percentages

#         # Calculate SR(ic) as (weighted_sums[ic] / weighted_max_sums[ic]) * 100
#         for ic in weighted_sums:
#             weighted_sum = weighted_sums[ic]
#             weighted_max_sum = weighted_max_sums[ic]

#             if weighted_max_sum != 0:
#                 sr_percentage = (weighted_sum / weighted_max_sum) * 100
#             else:
#                 sr_percentage = 0  # Default to zero if division by zero risk

#             sr_impact_criteria[ic] = round(sr_percentage, 2)  # Round to two decimal places

#         # Calculate SRf scores for each key functionality
#         srf_scores = calculate_srf_scores(sr_impact_criteria)

#         # Calculate the total SRI score
#         total_sri = calculate_total_sri(srf_scores)

#         # Calculate the weighted sums for each domain
#         weighted_domain_sums = calculate_weighted_domain_sums(domain_impact_scores)
#         weighted_max_domain_sums = calculate_weighted_domain_sums(domain_max_scores)
        
#         # Calculate SR(d) for each domain
#         sr_domains = calculate_sr_domains(weighted_domain_sums, weighted_max_domain_sums)

#     except SQLAlchemyError as e:
#         raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

#     # Create the SRI result similar to the calculate_sri function
#     sri_result = {
#         "smart_readiness_scores": smart_readiness_scores,
#         "sr_impact_criteria": sr_impact_criteria,  
#         "sr_domains": sr_domains,
#         "srf_scores": srf_scores,
#         "total_sri": total_sri
#     }

#     # Populate domain_scores, impact_scores, and services with actual values
#     domain_scores = [{"domain": domain, "percentage": sr_domains[domain], "score": sr_domains[domain]} for domain in sr_domains]
    
#     impact_scores = [{"impact": ic, "percentage": sr_impact_criteria[ic], "score": sr_impact_criteria[ic]} for ic in sr_impact_criteria]
    
#     key_functionalities_scores = [{"key_functionality": kf, "percentage": srf_scores[kf]} for kf in srf_scores]
    
#     services = []
#     for service_code, levels in user_input.lev.items():
#         for level, percentage in levels.items():
#             services.append({
#                 "service_code": service_code,
#                 "level": int(level),
#                 "percentage": percentage
#             })
   
#     # Generate the formatted DST data
#     dst_format = DstFormat(
#         user=1,
#         input_sri=sri_result["total_sri"],
#         building_type=user_input.building_type,
#         zone=user_input.zone,
#         domain_scores=sr_domains,
#         impact_scores=sr_impact_criteria,
#         key_functionalities_scores=srf_scores,
#         services=services
#     )

#     # Log the dst_format to inspect
#     print("dst_format:", dst_format)

#     # Save the dst_format to JSON
#     dst_format_filename = f"dst_format_building_xxx.json"
#     dst_format_file_path = os.path.join(save_path, dst_format_filename)

#     try:
#         # Save the dst_format as JSON
#         with open(dst_format_file_path, "w") as json_file:
#             json.dump(dst_format.dict(), json_file, indent=4)  # Convert Pydantic model to a dict and save it as JSON
        
#         print(f"DST format data saved to {dst_format_file_path}")
    
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to save DST format as JSON: {str(e)}")

#     # Save the generated dst_format in-memory (could be to a database or file)
#     dst_format_store[building_id] = dst_format    

#     # Return the formatted data for DST
#     return dst_format

@api_router.post("/possible_upgrades/{building_id}/", response_model=dict)
def possible_upgrades(building_id: int, user_input: SRIInput):
    logging.info(f"Processing possible upgrades for building {building_id}")

    try:
        # Validate the user input
        validate_numeric_data(user_input.lev)

        # Perform calculations for SRI
        calculated_scores = calculate_scores(user_input)
        weighted_sums = calculate_weighted_sums(user_input, calculated_scores["domain_impact_scores"])
        weighted_max_sums = calculate_weighted_sums(user_input, calculated_scores["domain_max_scores"])

        sr_impact_criteria = {
            ic: round((weighted_sums[ic] / weighted_max_sums[ic]) * 100, 2)
            if weighted_max_sums[ic] != 0 else 0
            for ic in weighted_sums
        }

        srf_scores = calculate_srf_scores(sr_impact_criteria)
        total_sri = calculate_total_sri(srf_scores)

        sr_domains = calculate_sr_domains(
            calculate_weighted_domain_sums(calculated_scores["domain_impact_scores"]),
            calculate_weighted_domain_sums(calculated_scores["domain_max_scores"])
        )

        services = [
            {"service_code": code, "level": int(level), "percentage": percent}
            for code, levels in user_input.lev.items()
            for level, percent in levels.items()
        ]

        # Generate the raw DST format
        dst_format = {
            "user": 1,
            "input_sri": total_sri,
            "building_type": user_input.building_type,
            "zone": user_input.zone,
            "domain_scores": sr_domains,
            "impact_scores": sr_impact_criteria,
            "key_functionalities_scores": srf_scores,
            "services": services,
        }

        logging.info(f"Generated raw DST format: {dst_format}")

        # Send the raw DST format to the second tool
        try:
            # Step 1: Authenticate to get the token
            auth_url = "https://buildon-sri.epu.ntua.gr/api/token"  # Replace with actual endpoint
            auth_credentials = {"username": "john", "password": "jpjpjp"}  # Replace with actual credentials

            login_response = requests.post(auth_url, data=auth_credentials)
            if login_response.status_code != 200:
                logging.error(f"Authentication failed with the DST: {login_response.content}")
                raise HTTPException(status_code=500, detail="Authentication failed with the DST.")

            token = login_response.json().get("access_token")

            # Step 2: Send the dst_format with the token
            headers = {"Authorization": f"Bearer {token}"}
            dst_url = "https://buildon-sri.epu.ntua.gr/dss/set/srigoal/"
            dst_response = requests.post(dst_url, json=dst_format, headers=headers)

            if dst_response.status_code != 200:
                logging.error(f"The DST rejected the data: {dst_response.content}")
                raise HTTPException(status_code=500, detail="Failed to send data to the DST.")

            logging.info(f"Successfully sent data to the DST for building {building_id}")
            return dst_format
        
            # auth_credentials = {"username": "john", "password": "jpjpjp"}
            # login_url = "http://second-tool.local/api/token"
            # login_response = requests.post(login_url, data=auth_credentials)

            # if login_response.status_code != 200:
            #     logging.error(f"Failed to authenticate with the second tool: {login_response.content}")
            #     raise HTTPException(status_code=500, detail="Authentication failed with the second tool.")

            # token = login_response.json().get("access_token")
            # headers = {"Authorization": f"Bearer {token}"}

            # dst_response = requests.post(
            #     "http://second-tool.local/api/receive-sri",
            #     json=dst_format,
            #     headers=headers,
            # )

            # if dst_response.status_code != 200:
            #     logging.error(f"The second tool rejected the data: {dst_response.content}")
            #     raise HTTPException(status_code=500, detail="Failed to send data to the second tool.")

            # logging.info(f"Successfully sent data to the second tool for building {building_id}")
            # return dst_format  # Optionally return the raw `dst_format`

        except requests.RequestException as e:
            logging.error(f"Error connecting to the second tool: {e}")
            raise HTTPException(status_code=500, detail="Could not connect to the second tool.")

    except SQLAlchemyError as e:
        logging.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

        # # Return the raw DST format for further processing
        # return dst_format

        # # Transform the raw DST format into the final expected format
        # transformed_data = transform_dst_format(dst_format)

        # # Send the transformed data to BuildON DST
        # try:
        #     auth_credentials = {"username": "john", "password": "jpjpjp"}
        #     login_url = "http://localhost:8000/token"
        #     login_response = requests.post(login_url, data=auth_credentials)

        #     if login_response.status_code != 200:
        #         logging.error(f"Failed to authenticate with BuildON DST: {login_response.content}")
        #         raise HTTPException(status_code=500, detail="Authentication failed with BuildON DST.")

        #     token = login_response.json().get("access_token")
        #     headers = {"Authorization": f"Bearer {token}"}

        #     dst_response = requests.post(
        #         "http://buildon-dst.local/api/receive-sri",  # Replace with actual BuildON DST endpoint
        #         json=transformed_data,
        #         headers=headers,
        #     )

        #     if dst_response.status_code != 200:
        #         logging.error(f"BuildON DST rejected the data: {dst_response.content}")
        #         raise HTTPException(status_code=500, detail="Failed to send data to BuildON DST.")

        #     logging.info(f"Successfully sent data to BuildON DST for building {building_id}")
        #     return transformed_data  # Optionally return what was sent

        # except requests.RequestException as e:
        #     logging.error(f"Error connecting to BuildON DST: {e}")
        #     raise HTTPException(status_code=500, detail="Could not connect to BuildON DST.")

    # except SQLAlchemyError as e:
    #     logging.error(f"Database error: {e}")
    #     raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    # except Exception as e:
    #     logging.error(f"Unexpected error: {e}")
    #     raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")




# @api_router.get("/upgrade-scenarios/{building_id}/", response_model=DstFormat)
# def get_dst_format(building_id: int):
#     # Check if the dst_format exists for the given building_id
#     if building_id not in dst_format_store:
#         raise HTTPException(status_code=404, detail="DST format not found for the given building ID")
    
#     # Retrieve the stored dst_format
#     return dst_format_store[building_id]


@api_router.post("/upgrade-scenarios/{building_id}/", response_model=DstFormat)
def post_dst_format(building_id: int, user_input: SRIInput):
    """
    Process and save SRI data and return dst_format.
    """
    try:
        validate_numeric_data(user_input.lev)
        
        # Perform calculations for SRI
        calculated_scores = calculate_scores(user_input)
        weighted_sums = calculate_weighted_sums(user_input, calculated_scores["domain_impact_scores"])
        weighted_max_sums = calculate_weighted_sums(user_input, calculated_scores["domain_max_scores"])

        sr_impact_criteria = {
            ic: round((weighted_sums[ic] / weighted_max_sums[ic]) * 100, 2)
            if weighted_max_sums[ic] != 0 else 0
            for ic in weighted_sums
        }

        srf_scores = calculate_srf_scores(sr_impact_criteria)
        total_sri = calculate_total_sri(srf_scores)

        sr_domains = calculate_sr_domains(
            calculate_weighted_domain_sums(calculated_scores["domain_impact_scores"]),
            calculate_weighted_domain_sums(calculated_scores["domain_max_scores"])
        )

        services = [
            {"service_code": code, "level": int(level), "percentage": percent}
            for code, levels in user_input.lev.items()
            for level, percent in levels.items()
        ]

        dst_format = {
            "user": 1,
            "input_sri": total_sri,
            "building_type": user_input.building_type,
            "zone": user_input.zone,
            "domain_scores": sr_domains,
            "impact_scores": sr_impact_criteria,
            "key_functionalities_scores": srf_scores,
            "services": services,
        }

        # Store the dst_format in memory
        dst_format_store[building_id] = dst_format

        return dst_format

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@api_router.get("/upgrade-scenarios/{building_id}/", response_model=DstFormat)
def get_dst_format(building_id: int):
    """
    Retrieve pre-calculated DST format for a given building ID.
    """
    if building_id not in dst_format_store:
        raise HTTPException(status_code=404, detail="DST format not found for the given building ID")
    
    return dst_format_store[building_id]


    
# Router /api
app.include_router(api_router)