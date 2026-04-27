# Architecture Documentation

## System Overview

The BuildON SRI Tools platform consists of two integrated web applications that together provide a complete workflow from building smartness assessment to upgrade planning. The tools follow a microservices-oriented architecture where each service maintains independent data storage but communicates via RESTful APIs.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        End User (Web Browser)                           │
└────────────┬────────────────────────────────────────┬───────────────────┘
             │                                        │
             │ HTTP/HTTPS                             │ HTTP/HTTPS
             ▼                                        ▼
┌────────────────────────────────┐      ┌────────────────────────────────┐
│     SRI Calculator Service     │      │      SMURF Service             │
│         (Port 3000/8000)       │      │        (Port 8080)             │
├────────────────────────────────┤      ├────────────────────────────────┤
│                                │      │                                │
│  ┌──────────────────────────┐ │      │  ┌──────────────────────────┐ │
│  │   React Frontend         │ │      │  │  Django Templates        │ │
│  │   (Presentation Layer)   │ │      │  │  (Presentation Layer)    │ │
│  │                          │ │      │  │                          │ │
│  │  • Semantic UI           │ │      │  │  • Bootstrap             │ │
│  │  • Bootstrap             │ │      │  │  • Highcharts            │ │
│  │  • Highcharts            │ │      │  │  • Custom CSS/JS         │ │
│  │  • Axios (HTTP)          │ │      │  │                          │ │
│  └────────┬─────────────────┘ │      │  └────────┬─────────────────┘ │
│           │ REST API           │      │           │ Django Views     │
│           ▼                    │      │           ▼                  │
│  ┌──────────────────────────┐ │      │  ┌──────────────────────────┐ │
│  │   FastAPI Application    │ │◄────┼──┤  Django Application      │ │
│  │   (Application Layer)    │ │ API │  │  (Application Layer)     │ │
│  │                          │ │     │  │                          │ │
│  │  • User authentication   │ │     │  │  • Scenario engine       │ │
│  │  • SRI calculation       │ │     │  │  • Technology matching   │ │
│  │  • Domain/service logic  │ │     │  │  • Cost calculation      │ │
│  │  • Score aggregation     │ │     │  │  • Ranking algorithms    │ │
│  │  • SQLModel ORM          │ │     │  │  • Django ORM            │ │
│  └────────┬─────────────────┘ │      │  └────────┬─────────────────┘ │
│           │ SQLAlchemy         │      │           │ Django ORM       │
│           ▼                    │      │           ▼                  │
│  ┌──────────────────────────┐ │      │  ┌──────────────────────────┐ │
│  │  PostgreSQL Database     │ │      │  │  PostgreSQL Database     │ │
│  │  (Persistence Layer)     │ │      │  │  (Persistence Layer)     │ │
│  │                          │ │      │  │                          │ │
│  │  • User accounts         │ │      │  │  • Technology catalogue  │ │
│  │  • Building profiles     │ │      │  │  • Equipment specs/costs │ │
│  │  • Service configs       │ │      │  │  • SRI parameters        │ │
│  │  • Assessment results    │ │      │  │  • Scenario cache        │ │
│  │  • Domain/impact scores  │ │      │  │  • Environmental data    │ │
│  └──────────────────────────┘ │      │  └──────────────────────────┘ │
│                                │      │                                │
└────────────────────────────────┘      └────────────────────────────────┘
```

## Component Architecture

### 1. SRI Calculator

**Technology Stack:**
- **Frontend**: ReactJS + Semantic UI + Bootstrap
- **Backend**: FastAPI (Python)
- **ORM**: SQLModel + SQLAlchemy
- **Database**: PostgreSQL
- **Visualization**: Highcharts
- **HTTP Client**: Axios

**Key Components:**

#### Frontend Layer (React)
```
src/
├── components/           # Reusable UI components
│   ├── DomainSelector.jsx
│   ├── ServiceLevelForm.jsx
│   ├── ScoreVisualization.jsx
│   └── NavigationBar.jsx
├── pages/                # Route-based page components
│   ├── Dashboard.jsx
│   ├── Assessment.jsx
│   ├── Results.jsx
│   └── Buildings.jsx
├── services/             # API integration layer
│   ├── api.js            # Axios configuration
│   ├── authService.js    # Authentication
│   └── assessmentService.js
└── utils/                # Helper functions
    ├── sriCalculations.js
    └── chartConfig.js
```

#### Backend Layer (FastAPI)
```python
# Core modules
main.py                   # Application entry point, route definitions
models.py                 # SQLModel database models
db_init.py                # Database initialization

# Data flow
User Request → FastAPI Endpoint → Business Logic → ORM → Database
Database → ORM → Response Serialization → JSON Response
```

**Key Endpoints:**
- `POST /auth/register`, `/auth/login` – Authentication
- `GET/POST /buildings` – Building management
- `POST /assessments` – Create assessment
- `GET /assessments/{id}/scores` – Retrieve results
- `GET /assessments/{id}/export` – Export for SMURF

#### Database Schema (Simplified)

```
users
├── id (PK)
├── email
├── password_hash
└── created_at

buildings
├── id (PK)
├── user_id (FK)
├── name
├── location
├── floor_area
└── construction_year

assessments
├── id (PK)
├── building_id (FK)
├── overall_sri
├── created_at
└── updated_at

assessment_services
├── id (PK)
├── assessment_id (FK)
├── service_id
├── functionality_level
├── share
└── applicable

domain_scores
├── id (PK)
├── assessment_id (FK)
├── domain_name
└── score

impact_scores
├── id (PK)
├── assessment_id (FK)
├── criterion_name
└── score
```

### 2. SMURF

**Technology Stack:**
- **Framework**: Django 4.2+
- **Frontend**: Django Templates + Bootstrap
- **Database**: PostgreSQL
- **Visualization**: Highcharts
- **Backend**: Python 3.10+

**Key Components:**

#### Application Structure
```
smurf_web_app/
├── models.py             # Database models
│   ├── CostTech          # Equipment catalogue
│   ├── Service           # Service definitions
│   ├── Domain            # Domain weights
│   ├── Impact            # Impact criteria
│   └── Level             # Functionality levels
├── views.py              # Request handlers
│   ├── landing_view()
│   ├── set_sri_goal()
│   ├── generate_scenarios()
│   └── scenario_results()
├── scenarios.py          # Scenario generation engine
│   ├── ScenarioGenerator
│   ├── TechnologyMatcher
│   ├── CostCalculator
│   └── SRIProjector
├── csvhandle.py          # Data import utilities
└── singularhandle.py     # Single-building logic
```

#### Database Schema (Simplified)

```
cost_techs                # Technology catalogue
├── id (PK)
├── service_id
├── functionality_level
├── equipment_name
├── manufacturer
├── cost_eur
├── installation_cost
├── power_consumption_w
├── efficiency_class
├── co2_kg_year
└── lifespan_years

services
├── id (PK)
├── service_code          # e.g., "H1", "C2"
├── domain_id (FK)
├── description
└── max_functionality_level

domains
├── id (PK)
├── name                  # e.g., "Heating"
├── code                  # e.g., "HTG"
└── weight

impacts
├── id (PK)
├── name                  # e.g., "Energy efficiency"
├── code
└── weight

levels
├── id (PK)
├── service_id (FK)
├── level_number          # 0-4
└── description
```

## Data Flow

### Assessment Workflow (SRI Calculator)

```
1. User Registration/Login
   ↓
2. Create Building Profile
   ↓
3. Select Technical Domains ──────────┐
   ↓                                  │
4. For each domain:                   │
   ├─ Select applicable services      │
   ├─ Assign functionality levels     │
   └─ Set coverage percentage         │
   ↓                                  │
5. Submit Assessment                  │
   ↓                                  │
6. Backend Processing:                │
   ├─ Validate inputs                 │
   ├─ Load domain weights ────────────┘
   ├─ Load impact weights
   ├─ Calculate service scores
   ├─ Aggregate domain scores
   ├─ Aggregate impact scores
   ├─ Calculate overall SRI
   └─ Store results in database
   ↓
7. Display Results Dashboard
   ├─ Overall SRI score & class
   ├─ Domain breakdown
   ├─ Impact criteria scores
   └─ Key functionality scores
   ↓
8. Optional: Export to SMURF
```

### Upgrade Planning Workflow (SMURF)

```
1. Import Baseline Assessment
   ├─ Manual JSON upload
   └─ API call to SRI Calculator
   ↓
2. User Sets Target SRI Score
   ↓
3. Scenario Generation Engine:
   ├─ Gap Analysis
   │  ├─ Compare current vs max functionality per service
   │  ├─ Identify services with highest impact potential
   │  └─ Calculate required SRI increase per domain
   ├─ Technology Matching
   │  ├─ Query catalogue for compatible equipment
   │  ├─ Filter by functionality level support
   │  └─ Retrieve cost and specifications
   ├─ Scenario Composition
   │  ├─ Generate single-service upgrades
   │  ├─ Generate multi-service combinations
   │  ├─ Consider budget constraints
   │  └─ Optimize for target SRI
   ├─ Impact Calculation
   │  ├─ Project post-upgrade SRI scores
   │  ├─ Calculate total costs
   │  ├─ Compute cost-effectiveness
   │  └─ Estimate environmental impact
   └─ Ranking
      ├─ By total SRI gain
      ├─ By total cost
      └─ By cost-effectiveness
   ↓
4. Display Scenario Comparison Dashboard
   ├─ Ranked scenario list
   ├─ Baseline vs upgrade visualizations
   ├─ Equipment recommendations
   ├─ Cost breakdown
   └─ Environmental impact
   ↓
5. User Selects Preferred Scenario
   ↓
6. Export Results (JSON/PDF)
```

## API Integration Between Tools

### SRI Calculator → SMURF

**Endpoint**: `GET /assessments/{id}/export`

**Response Format**:
```json
{
  "building_id": 123,
  "building_name": "Office Building A",
  "assessment_id": 456,
  "overall_sri": 45.2,
  "sri_class": "C",
  "domains": {
    "heating": {
      "score": 50.0,
      "services": [
        {
          "service_id": "H1",
          "service_name": "Weather prediction controls",
          "functionality_level": 1,
          "share": 100,
          "applicable": true
        }
      ]
    },
    "cooling": {
      "score": 40.0,
      "services": [...]
    }
  },
  "impact_criteria": {
    "energy_efficiency": 48.5,
    "comfort": 42.0,
    "convenience": 50.0,
    "health_wellbeing": 45.0,
    "maintenance": 40.0,
    "information": 38.0,
    "energy_flexibility": 35.0
  },
  "key_functionalities": {
    "energy_performance": 46.0,
    "response_to_user_needs": 43.0,
    "energy_flexibility": 35.0
  }
}
```

### SMURF → SRI Calculator (Authentication)

SMURF may use API tokens for authentication:

```python
headers = {
    "Authorization": f"Bearer {access_token}"
}
response = requests.get(
    f"{SRI_CALCULATOR_URL}/assessments/{assessment_id}/export",
    headers=headers
)
```

## Deployment Architecture

### Docker-Based Deployment

```
Docker Host
├── Docker Network: sri-net
│
├── Container: sri-calculator-backend
│   ├── Image: Python 3.10 + FastAPI
│   ├── Port: 8000
│   └── Volumes: ./SRI-calculator-main:/app
│
├── Container: sri-calculator-frontend
│   ├── Image: Node 18 + React
│   ├── Port: 3000
│   └── Volumes: ./SRI-calculator-main/sri-frontend:/app
│
├── Container: sri-calculator-db
│   ├── Image: PostgreSQL 14
│   ├── Port: 5432
│   └── Volumes: postgres-data-sri:/var/lib/postgresql/data
│
├── Container: smurf-web
│   ├── Image: Python 3.10 + Django
│   ├── Port: 8080
│   └── Volumes: ./smurf_web:/app
│
└── Container: smurf-db
    ├── Image: PostgreSQL 14
    ├── Port: 5433 (mapped to avoid conflict)
    └── Volumes: postgres-data-smurf:/var/lib/postgresql/data
```

### Production Deployment Considerations

**Recommended setup for production**:

1. **Reverse Proxy** (e.g., Nginx)
   - SSL/TLS termination
   - Load balancing
   - Static file serving

2. **Application Servers**
   - SRI Calculator Backend: Uvicorn with multiple workers
   - SMURF: Gunicorn with multiple workers

3. **Database**
   - Separate PostgreSQL instances or single instance with separate databases
   - Regular backups
   - Connection pooling

4. **Security**
   - Environment-based configuration (no hardcoded secrets)
   - HTTPS enforcement
   - CORS configuration
   - Rate limiting
   - Input validation

5. **Monitoring**
   - Application logs
   - Database query performance
   - API response times
   - Error tracking (e.g., Sentry)

Example Nginx configuration:

```nginx
server {
    listen 80;
    server_name sri-tools.example.com;

    location /smurf {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Scalability Considerations

### Horizontal Scaling

Both services can be scaled horizontally:

```
Load Balancer
├── SRI Calculator Instance 1
├── SRI Calculator Instance 2
└── SRI Calculator Instance N

Load Balancer
├── SMURF Instance 1
├── SMURF Instance 2
└── SMURF Instance N

Shared PostgreSQL Cluster
```

### Caching Strategy

- **Frontend**: Browser caching for static assets
- **Backend**: Redis for session data and frequently-accessed methodology parameters
- **Database**: Query result caching for domain/impact weights

### Database Optimization

- Indexed columns: `user_id`, `building_id`, `assessment_id`, `service_id`
- Partitioning for large assessment datasets
- Read replicas for reporting queries

## Security Architecture

### Authentication Flow

```
1. User submits credentials
   ↓
2. Backend validates against database
   ↓
3. Generate JWT token (FastAPI) or session (Django)
   ↓
4. Return token to frontend
   ↓
5. Frontend stores token (localStorage/sessionStorage)
   ↓
6. Include token in Authorization header for subsequent requests
   ↓
7. Backend validates token on each request
```

### Data Protection

- **Passwords**: Hashed using bcrypt/argon2
- **API Tokens**: JWT with expiration
- **Database**: Encrypted connections (SSL)
- **Sensitive Data**: Encrypted at rest

### Access Control

- **SRI Calculator**: User can only access own buildings/assessments
- **SMURF**: Session-based access control
- **Admin Panels**: Role-based access (Django admin, future FastAPI admin)

## Technology Decisions & Rationale

| Decision | Rationale |
|----------|-----------|
| **FastAPI for SRI Calculator** | Modern, async, automatic API docs, type hints |
| **Django for SMURF** | Mature ORM, admin panel, template engine for quick prototyping |
| **PostgreSQL** | ACID compliance, JSON support, mature ecosystem |
| **React for SRI Calculator UI** | Component-based, large ecosystem, good for complex SPAs |
| **Django Templates for SMURF** | Simpler than SPA for form-heavy workflow, server-side rendering |
| **Docker** | Reproducible environments, easy deployment |
| **Separate databases** | Service independence, easier backup/restore per service |
| **RESTful API** | Standard, well-understood, language-agnostic |

---

**Maintained by**: Decision Support Systems Laboratory, NTUA  
**Last Updated**: April 2025
