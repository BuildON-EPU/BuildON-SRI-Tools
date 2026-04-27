# SRI Calculator

**Automated Smart Readiness Indicator (SRI) Assessment Tool**

Part of the [BuildON SRI Tools](../README.md) platform.

## Overview

The SRI Calculator is a web-based tool that automates the assessment of building smartness according to Commission Delegated Regulation (EU) 2020/2155. It provides a guided workflow for evaluating smart-ready services across nine technical domains and calculates SRI scores with interactive visualizations.

## Features

- **Automated SRI Assessment** – Implements official SRI methodology
- **Guided Workflow** – Step-by-step domain and service selection
- **Multi-Dimensional Results** – Overall, domain, impact criteria, and key functionality scores
- **Interactive Visualizations** – Highcharts-powered dashboards
- **Database Persistence** – Track assessment history with PostgreSQL
- **API-First Design** – RESTful API for integration with SMURF and other tools
- **User Management** – Authentication and multi-user support

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Backend Framework | FastAPI |
| Frontend Framework | ReactJS |
| ORM | SQLModel + SQLAlchemy |
| Database | PostgreSQL |
| UI Components | Semantic UI, Bootstrap |
| Visualization | Highcharts |
| HTTP Client | Axios |

## Architecture

```
┌─────────────────────────────────────────────────┐
│              SRI Calculator                     │
├─────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────┐ │
│  │    React Frontend (Port 3000)             │ │
│  │    - Semantic UI, Bootstrap               │ │
│  │    - Highcharts for visualization         │ │
│  │    - Axios for API communication          │ │
│  └───────────────────────────────────────────┘ │
│                      ▼                          │
│  ┌───────────────────────────────────────────┐ │
│  │    FastAPI Backend (Port 8000)            │ │
│  │    - RESTful API endpoints                │ │
│  │    - SRI calculation engine               │ │
│  │    - User authentication                  │ │
│  │    - SQLModel ORM                         │ │
│  └───────────────────────────────────────────┘ │
│                      ▼                          │
│  ┌───────────────────────────────────────────┐ │
│  │    PostgreSQL Database (Port 5432)        │ │
│  │    - User accounts & buildings            │ │
│  │    - Service configurations               │ │
│  │    - SRI assessment results               │ │
│  └───────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

## Prerequisites

### Docker Installation (Recommended)

- Docker (≥20.10)
- Docker Compose (≥1.29)
- 2GB RAM minimum
- Ports 3000, 8000, 5432 available

### Manual Installation

- Python 3.10+
- Node.js 18+ with npm
- PostgreSQL 14+

## Quick Start with Docker

### 1. Create Docker Network

```bash
docker network create sri-net
```

### 2. Build and Start Services

```bash
docker-compose up --build
```

This command will:
- Build Docker images for backend, frontend, and database
- Start all services
- Initialize the database schema
- Make the application available at:
  - **Frontend**: [http://localhost:3000](http://localhost:3000)
  - **Backend API**: [http://localhost:8000](http://localhost:8000)
  - **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. Initialize Database (First Time Only)

```bash
docker-compose exec backend python db_init.py
```

### 4. Stop Services

```bash
docker-compose down
```

## Manual Installation (Development)

### Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure database connection (create .env file)
cat > .env << EOF
DATABASE_URL=postgresql://admin:admin!@localhost:5432/buildon_sri_db
SECRET_KEY=your-secret-key-here
EOF

# Run database migrations
alembic upgrade head

# Start backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd sri-frontend

# Install dependencies
npm install

# Start development server
npm start
```

The frontend will be available at [http://localhost:3000](http://localhost:3000).

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Database Configuration
DATABASE_URL=postgresql://admin:admin!@localhost:5432/buildon_sri_db

# Application Settings
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Settings (for development)
ALLOWED_ORIGINS=http://localhost:3000
```

## Project Structure

```
SRI-calculator-main/
├── main.py                      # FastAPI application entry point
├── models.py                    # SQLModel database models
├── db_init.py                   # Database initialization script
├── requirements.txt             # Python dependencies
├── docker-compose.yml           # Docker orchestration
├── Dockerfile                   # Backend container definition
├── alembic.ini                  # Database migration config
│
├── alembic/                     # Database migrations
│   ├── env.py                   # Migration environment
│   └── versions/                # Migration scripts
│       ├── 2024_07_06_0940-e7d6d985752c_*.py
│       ├── 2024_07_12_1837-1dcbb9c8666d_*.py
│       └── ...
│
├── Classes_CSV/                 # SRI Methodology Reference Data
│   ├── domain_w.csv             # Domain weights
│   ├── impact_w.csv             # Impact criteria weights
│   ├── levels_new.csv           # Functionality level definitions
│   └── services.csv             # Smart-ready services catalogue
│
└── sri-frontend/                # React frontend application
    ├── package.json             # Node.js dependencies
    ├── Dockerfile_front         # Frontend container definition
    ├── public/                  # Static assets
    │   └── index.html
    └── src/                     # React components and logic
        ├── components/          # Reusable UI components
        ├── pages/               # Page components
        ├── services/            # API service layer
        └── App.js               # Main application component
```

## API Documentation

### Accessing API Documentation

The FastAPI backend provides automatic interactive API documentation:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Key Endpoints

#### Authentication

- `POST /auth/register` – Register new user
- `POST /auth/login` – User login (returns JWT token)

#### Buildings

- `GET /buildings` – List all buildings for authenticated user
- `POST /buildings` – Create new building
- `GET /buildings/{id}` – Get building details
- `PUT /buildings/{id}` – Update building information
- `DELETE /buildings/{id}` – Delete building

#### SRI Assessment

- `POST /assessments` – Create new SRI assessment
- `GET /assessments/{id}` – Get assessment results
- `PUT /assessments/{id}` – Update assessment
- `GET /assessments/{id}/scores` – Get detailed scores (domain, impact criteria, key functionalities)

#### Services

- `GET /services` – List all smart-ready services
- `GET /services/domains` – List technical domains
- `POST /assessments/{id}/services` – Assign service functionality levels

## Usage Workflow

### 1. Register and Login

Create an account and authenticate to access the platform.

### 2. Create Building Profile

Define building metadata:
- Building name and location
- Type (residential, commercial, etc.)
- Floor area
- Construction year

### 3. Select Technical Domains

Choose applicable domains from:
- Heating
- Cooling
- Domestic Hot Water
- Ventilation
- Lighting
- Electricity
- Electric Vehicle Charging
- Monitoring and Control
- Dynamic Building Envelope

### 4. Assign Service Functionality Levels

For each domain, evaluate smart-ready services by:
- Marking service as applicable/not applicable
- Selecting current functionality level (0-4)
- Specifying percentage of building affected

### 5. View Results

Explore interactive dashboards showing:
- **Overall SRI Score and Class** (0-100%)
- **Domain-Level Scores** – Performance per technical domain
- **Impact Criteria Scores** – Energy savings, comfort, convenience, health & wellbeing, maintenance, information to occupants, energy flexibility
- **Key Functionality Scores** – Energy performance, response to user needs, energy flexibility

### 6. Export to SMURF 

Transfer baseline assessment to SMURF for upgrade scenario generation.

## SRI Methodology Reference

The tool implements the official SRI methodology defined in:

**Commission Delegated Regulation (EU) 2020/2155**  
[https://eur-lex.europa.eu/eli/reg_del/2020/2155/oj](https://eur-lex.europa.eu/eli/reg_del/2020/2155/oj)

Key methodology files are located in `Classes_CSV/`:

- `domain_w.csv` – Domain weighting factors
- `impact_w.csv` – Impact criteria weighting factors
- `services.csv` – Smart-ready services definitions
- `levels_new.csv` – Functionality level descriptions

## Troubleshooting

### Port Conflicts

If ports 3000, 8000, or 5432 are in use:

```bash
# Check what's using a port (macOS/Linux)
lsof -i :3000

# Modify docker-compose.yml to use different ports
```

### Database Connection Issues

```bash
# Verify PostgreSQL is running
docker-compose ps

# Check database logs
docker-compose logs db

# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up --build
```

### Frontend Build Errors

```bash
# Clear node_modules and rebuild
cd sri-frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

### Backend Import Errors

```bash
# Reinstall Python dependencies
pip install --upgrade -r requirements.txt

# Check Python version
python --version  # Should be 3.10+
```

## Testing

### Run Backend Tests

```bash
pytest tests/ -v
```

### Run Frontend Tests

```bash
cd sri-frontend
npm test
```

## Integration with SMURF

The SRI Calculator is designed to work seamlessly with SMURF:

1. Complete SRI assessment in SRI Calculator
2. Results are stored with unique assessment ID
3. SMURF retrieves baseline data via RESTful API
4. User defines target SRI score in SMURF
5. SMURF generates upgrade scenarios

API endpoint for SMURF integration:

```
GET /assessments/{id}/export
```

Returns structured JSON with:
- Domain scores and service configurations
- Functionality levels per service
- Impact criteria breakdown

## License

This project is licensed under the MIT License - see [LICENSE](../LICENSE).

## Support

- **Email**: gpapias@epu.ntua.gr
- **Documentation**: [Main README](../README.md)

## Acknowledgments

This tool was developed within the framework of:

- **BuildON Project** – Horizon Europe Grant Agreement No. 101104141
- **SRI-ENACT Project** – LIFE Programme Grant Agreement No. 101077201

Developed by the Decision Support Systems Laboratory, National Technical University of Athens, Greece.

---

**Parent Project**: [BuildON SRI Tools](../README.md)