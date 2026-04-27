# BuildON SRI Tools

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com)
[![Django](https://img.shields.io/badge/Django-4.2+-092E20.svg)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://react.dev/)

**From Assessment to Action: Digital Tools for SRI Calculation and Smart Building Upgrade Planning**

> **Live Demo**: Try the tools online at [https://sri.buildon.epu.ntua.gr/](https://sri.buildon.epu.ntua.gr/)

This repository contains two integrated web-based tools for implementing the Smart Readiness Indicator (SRI) framework defined in Commission Delegated Regulation (EU) 2020/2155:

1. **SRI Calculator** – Automates end-to-end SRI assessment, from service selection to score visualization
2. **SMURF (Smart Building Readiness Assessment Tool)** – Transforms baseline SRI assessments into costed upgrade scenarios aligned with user-defined targets

The tools enable building owners, auditors, and facility managers to assess building smartness and explore realistic upgrade pathways with market-available technologies.

---

## Table of Contents

- [Live Demo](#live-demo)
- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Acknowledgments](#acknowledgments)
- [License](#license)
- [Contact](#contact)

---

## Live Demo

**Try the tools without installation:**

- **SRI Calculator & SMURF**: [https://sri.buildon.epu.ntua.gr/](https://sri.buildon.epu.ntua.gr/)

The hosted version is deployed on the BuildON project infrastructure and provides the same functionality as the local installation. Perfect for testing, demonstrations, and quick assessments.

**Note**: For production use, data privacy, or customization needs, we recommend deploying your own instance using the instructions below.

---

## Features

### SRI Calculator

- **Automated SRI Assessment**: Implements Commission Delegated Regulation (EU) 2020/2155
- **Guided Workflow**: Step-by-step interface for domain selection, service applicability, and functionality-level assignment
- **Multi-Dimensional Visualization**: Interactive dashboards showing overall scores, domain-level contributions, impact criteria, and key functionalities
- **Data Persistence**: PostgreSQL-backed storage for assessment history and comparison
- **Standards Compliance**: Follows official SRI methodology including domain and impact-criteria weighting

### SMURF (Smart Building Readiness Assessment Tool)

- **Target-Driven Upgrade Planning**: Generate scenarios to achieve user-defined SRI targets
- **Market-Grounded Solutions**: Links service upgrades to commercially available equipment with indicative costs
- **Multi-Criteria Ranking**: Compare scenarios by SRI gain, total cost, and cost-effectiveness
- **Environmental Impact**: Estimates carbon emissions for each upgrade pathway
- **Technology Catalogue**: Structured database of smart building systems with technical specifications
- **Integrated Workflow**: Seamlessly consumes baseline assessments from SRI Calculator via RESTful API

---

## Architecture

The platform follows a modular, microservices-oriented architecture with two independent but integrated web applications:

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface                           │
│                    (Browser-based access)                       │
└────────────┬────────────────────────────────────┬───────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────────┐      ┌────────────────────────────┐
│     SRI Calculator         │      │         SMURF              │
│                            │      │                            │
│  ┌──────────────────────┐ │      │  ┌──────────────────────┐ │
│  │   React Frontend     │ │      │  │  Django Templates    │ │
│  │ (Semantic UI,        │ │      │  │  (Bootstrap,         │ │
│  │  Bootstrap)          │ │      │  │   Highcharts)        │ │
│  └──────────────────────┘ │      │  └──────────────────────┘ │
│  ┌──────────────────────┐ │      │  ┌──────────────────────┐ │
│  │   FastAPI Backend    │ │◄────►│  │  Django Backend      │ │
│  │ (SRI Assessment      │ │ API  │  │ (Scenario Generation)│ │
│  │  Engine)             │ │      │  │                      │ │
│  └──────────────────────┘ │      │  └──────────────────────┘ │
│  ┌──────────────────────┐ │      │  ┌──────────────────────┐ │
│  │  PostgreSQL DB       │ │      │  │  PostgreSQL DB       │ │
│  │ (Assessments,        │ │      │  │ (Technology          │ │
│  │  Building Data)      │ │      │  │  Catalogue, Costs)   │ │
│  └──────────────────────┘ │      │  └──────────────────────┘ │
└────────────────────────────┘      └────────────────────────────┘
```

**Key Components:**

- **SRI Calculator**: FastAPI + React + PostgreSQL
- **SMURF**: Django + PostgreSQL + Equipment Database
- **Integration**: RESTful API for assessment data transfer
- **Deployment**: Docker containers for reproducible setup

---

## Quick Start

### Option 1: Use Hosted Version (No Installation)

The fastest way to try the tools:

**Visit**: [https://sri.buildon.epu.ntua.gr/](https://sri.buildon.epu.ntua.gr/)

- No installation required
- Register and start assessing immediately
- Fully functional SRI Calculator and SMURF
- Hosted on BuildON project infrastructure

### Option 2: Local Installation with Docker

For development, customization, or private deployment:

#### Prerequisites

- Docker (≥20.10)
- Docker Compose (≥1.29)
- 4GB RAM minimum
- Ports 3000, 8000, 8080 available

#### Launch Both Tools

```bash
# Clone the repository
git clone https://github.com/BuildON-EPU/BuildON-SRI-Tools
cd BuildON-SRI-Tools

# Start SRI Calculator
cd SRI-calculator-main
docker network create sri-net
docker-compose up --build -d

# Start SMURF (in a new terminal)
cd ../dst-SRI_DST_BuildON-prod/smurf_web
docker-compose up --build -d
```

**Access the tools:**

- SRI Calculator Frontend: [http://localhost:3000](http://localhost:3000)
- SRI Calculator API: [http://localhost:8000](http://localhost:8000)
- SMURF: [http://localhost:8080](http://localhost:8080/smurf)

---

## Installation

### Detailed Setup Instructions

#### 1. SRI Calculator

```bash
cd SRI-calculator-main

# Create Docker network
docker network create sri-net

# Configure environment (optional - defaults provided)
cp .env.example .env  # if available

# Build and start services
docker-compose up --build

# Initialize database (first-time only)
docker-compose exec backend python db_init.py
```

**Service Configuration:**

- Backend: Port 8000 (FastAPI)
- Frontend: Port 3000 (React)
- Database: Port 5432 (PostgreSQL)
  - Default user: `admin`
  - Default password: `admin!`
  - Default database: `buildon_sri_db`

#### 2. SMURF

```bash
cd dst-SRI_DST_BuildON-prod/smurf_web

# Build and start
docker-compose up --build -d

# Run initial migrations (first-time only)
docker-compose exec web python manage.py migrate

# Load technology catalogue
docker-compose exec web python fill_models.py
```

**Configuration:**

- Web Interface: Port 8080
- Database: Separate PostgreSQL instance for equipment catalogue

### Manual Installation (Development)

<details>
<summary>Click to expand manual setup instructions</summary>

#### SRI Calculator Backend

```bash
cd SRI-calculator-main
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure PostgreSQL connection in .env
python main.py
```

#### SRI Calculator Frontend

```bash
cd SRI-calculator-main/sri-frontend
npm install
npm start
```

#### SMURF

```bash
cd dst-SRI_DST_BuildON-prod/smurf_web
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python fill_models.py
python manage.py runserver 8080
```

</details>

---

## Usage

### Workflow Overview

1. **Assessment**: Use SRI Calculator to perform baseline SRI assessment
2. **Target Setting**: Transfer results to SMURF and define target SRI score
3. **Scenario Generation**: Review generated upgrade scenarios
4. **Comparison**: Evaluate options by cost, SRI gain, and cost-effectiveness
5. **Selection**: Choose preferred intervention pathway

### Step-by-Step Example

#### Step 1: Create Building Assessment (SRI Calculator)

1. Register/login at [http://localhost:3000](http://localhost:3000)
2. Create new building profile
3. Select applicable technical domains (heating, cooling, lighting, etc.)
4. For each domain, assign functionality levels to smart-ready services
5. Submit assessment and view results dashboard

**Key Outputs:**
- Overall SRI score and class
- Scores per technical domain
- Scores per impact criterion
- Key functionality scores

#### Step 2: Generate Upgrade Scenarios (SMURF)

1. Access SMURF at [http://localhost:8080/smurf](http://localhost:8080/smurf)
2. Import baseline assessment from SRI Calculator
3. Define target SRI score
4. Review generated scenarios ranked by:
   - Total SRI gain
   - Total cost
   - Cost-effectiveness (SRI gain per €)

**Scenario Details:**
- Service-level upgrades
- Market equipment recommendations
- Estimated investment costs
- Environmental impact indicators
- Post-upgrade SRI projections

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| **SRI Calculator** | |
| Backend Framework | FastAPI |
| Frontend Framework | ReactJS |
| ORM | SQLModel + SQLAlchemy |
| Database | PostgreSQL |
| UI Components | Semantic UI, Bootstrap |
| Visualization | Highcharts |
| HTTP Client | Axios |
| **SMURF** | |
| Web Framework | Django 4.2+ |
| Database | PostgreSQL |
| UI Components | Bootstrap |
| Visualization | Highcharts |
| **Deployment** | |
| Containerization | Docker |
| Orchestration | Docker Compose |
| **Development** | |
| Languages | Python 3.10+, JavaScript (ES6+) |
| Version Control | Git |

---

## Project Structure

```
BuildON-SRI-Tools/
├── README.md                          # This file
├── LICENSE                            # MIT License
├── CITATION.cff                       # Citation metadata
├── CONTRIBUTING.md                    # Contribution guidelines
│
├── SRI-calculator-main/               # SRI Calculator service
│   ├── main.py                        # FastAPI application entry point
│   ├── models.py                      # SQLModel database models
│   ├── requirements.txt               # Python dependencies
│   ├── docker-compose.yml             # Docker orchestration
│   ├── Dockerfile                     # Backend container definition
│   ├── db_init.py                     # Database initialization script
│   ├── alembic/                       # Database migration scripts
│   ├── sri-frontend/                  # React frontend application
│   │   ├── package.json               # Node.js dependencies
│   │   ├── Dockerfile_front           # Frontend container
│   │   ├── public/                    # Static assets
│   │   └── src/                       # React components
│   └── Classes_CSV/                   # SRI methodology reference data
│       ├── domain_w.csv               # Domain weights
│       ├── impact_w.csv               # Impact criteria weights
│       ├── levels_new.csv             # Functionality level definitions
│       └── services.csv               # Smart-ready services catalogue
│
└── dst-SRI_DST_BuildON-prod/          # SMURF service
    └── smurf_web/                     # Django application
        ├── manage.py                  # Django management script
        ├── requirements.txt           # Python dependencies
        ├── fill_models.py             # Technology catalogue loader
        ├── config/
        │   ├── docker-compose.yaml    # Docker orchestration
        │   ├── Dockerfile             # Container definition
        │   └── run.sh                 # Startup script
        ├── smurf_web/                 # Django project configuration
        │   ├── settings.py            # Application settings
        │   ├── urls.py                # URL routing
        │   └── wsgi.py                # WSGI entry point
        ├── smurf_web_app/             # Main application module
        │   ├── models.py              # Database models
        │   ├── views.py               # Request handlers
        │   ├── scenarios.py           # Scenario generation engine
        │   ├── csvhandle.py           # Data import utilities
        │   └── static/                # Static assets
        ├── templates/                 # HTML templates
        └── excel_files/               # Equipment catalogue data
            ├── domain_w.csv
            ├── impact_w.csv
            ├── services.csv
            ├── levels.csv
            └── costtechs*.csv         # Technology costs and specs
```

---

## Documentation

### Key Resources

- **SRI Methodology**: [Commission Delegated Regulation (EU) 2020/2155](https://eur-lex.europa.eu/eli/reg_del/2020/2155/oj)
- **API Documentation**: 
  - SRI Calculator: [http://localhost:8000/docs](http://localhost:8000/docs) (FastAPI Swagger UI)

### Additional Documentation

- [SRI Calculator README](SRI-calculator-main/README.md)
- [SMURF README](dst-SRI_DST_BuildON-prod/README.md)

### Related Projects

- [BuildON Project](https://buildon-project.eu/) (Horizon Europe Grant 101104141)
- [SRI-ENACT Project](https://www.sri-enact.eu/) (LIFE Programme Grant 101077201)

---

### Quick Contribution Guide

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup

See [Installation](#installation) section for development environment setup.

---

## Acknowledgments

This work was conducted within the framework of:

- **BuildON Project** – Horizon Europe Grant Agreement No. 101104141
- **SRI-ENACT Project** – LIFE Programme Grant Agreement No. 101077201

**Research Team:**
- [Decision Support Systems Laboratory](https://www.epu.ntua.gr), School of Electrical & Computer Engineering, National Technical University of Athens, Greece

The content is the sole responsibility of the authors and does not necessarily reflect the views of the European Commission.

### Pilot Deployments

The tools have been deployed and validated in pilot buildings across:
- 🇬🇷 Greece
- 🇪🇸 Spain
- 🇵🇱 Poland
- 🇫🇷 France
- 🇫🇮 Finland


---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Decision Support Systems Laboratory, NTUA

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files...
```

---

## Contact

**Corresponding Author**: Ioannis Papias  
**Email**: [gpapias@epu.ntua.gr](mailto:gpapias@epu.ntua.gr)  
**Institution**: National Technical University of Athens, Greece  
**Laboratory**: [Decision Support Systems Laboratory](https://www.epu.ntua.gr)

**Project Resources**:
- **Live Demo**: [https://sri.buildon.epu.ntua.gr/](https://sri.buildon.epu.ntua.gr/)
- **Repository**: [https://github.com/BuildON-EPU/BuildON-SRI-Tools](https://github.com/BuildON-EPU/BuildON-SRI-Tools)  

---

## Roadmap

### Current Version (v1.0.0)
- Automated SRI assessment
- Interactive visualization dashboards
- Scenario-based upgrade planning
- Market equipment catalogue
- Cost and environmental impact estimates

### Planned Features
- Region-specific cost databases
- Multi-building portfolio management
- Advanced interdependency analysis between systems
- Integration with national building databases
- Enhanced reporting and certification exports
- Machine learning-based scenario optimization
- Real-time equipment price updates via vendor APIs

---

## Known Limitations

- Cost estimates based on European market averages; regional variations may apply
- Technology catalogue requires periodic manual updates
- Scenario generation evaluates service-level upgrades independently (no cross-system dependency modeling)
- Installation constraints and site-specific factors not automatically considered

---

