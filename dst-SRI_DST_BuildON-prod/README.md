# SMURF (Smart Building Readiness Assessment Tool)

**Target-Driven SRI Upgrade Scenario Generation**

Part of the [BuildON SRI Tools](../README.md) platform.

## Overview

SMURF (Smart Building Readiness Assessment Tool) is a decision-support tool that transforms baseline SRI assessments into actionable, costed upgrade scenarios. It evaluates feasible service-level improvements, maps them to commercially available smart building technologies, and ranks scenarios according to SRI gain, cost, and cost-effectiveness.

## Features

- **Target-Driven Planning** – Generate scenarios to achieve user-defined SRI targets
- **Market-Grounded Solutions** – Links upgrades to real equipment with indicative costs
- **Multi-Criteria Ranking** – Compare by SRI gain, total cost, cost-effectiveness
- **Technology Catalogue** – Structured database of smart building systems and controls
- **Environmental Impact** – Estimates carbon emissions and energy consumption
- **Integrated Workflow** – Seamlessly imports baseline assessments from SRI Calculator
- **Interactive Comparison** – Visualize baseline vs. post-upgrade SRI profiles

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Web Framework | Django 4.2+ |
| Database | PostgreSQL |
| UI Components | Bootstrap, Django Templates |
| Visualization | Highcharts |
| Backend Logic | Python 3.10+ |

## Architecture

```
┌──────────────────────────────────────────────────┐
│                    SMURF                         │
├──────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────┐ │
│  │    Django Templates (Bootstrap)            │ │
│  │    - Target setting interface              │ │
│  │    - Scenario comparison dashboard         │ │
│  │    - Highcharts visualizations             │ │
│  └────────────────────────────────────────────┘ │
│                      ▼                           │
│  ┌────────────────────────────────────────────┐ │
│  │    Django Backend (Port 8080)              │ │
│  │    - Scenario generation engine            │ │
│  │    - API integration with SRI Calculator   │ │
│  │    - Cost calculation logic                │ │
│  │    - Technology matching algorithm         │ │
│  └────────────────────────────────────────────┘ │
│                      ▼                           │
│  ┌────────────────────────────────────────────┐ │
│  │    PostgreSQL Database                     │ │
│  │    - Technology catalogue                  │ │
│  │    - Equipment specifications & costs      │ │
│  │    - SRI methodology parameters            │ │
│  │    - Environmental indicators              │ │
│  └────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘
           ▲
           │ RESTful API
           │ (baseline SRI data)
           │
┌──────────────────────────────────────────────────┐
│          SRI Calculator                          │
│      (baseline assessment source)                │
└──────────────────────────────────────────────────┘
```

## Prerequisites

### Docker Installation (Recommended)

- Docker (≥20.10)
- Docker Compose (≥1.29)
- 2GB RAM minimum
- Port 8080 available

### Manual Installation

- Python 3.10+
- PostgreSQL 14+
- Access to SRI Calculator instance (for assessment import)

## Quick Start with Docker

### 1. Navigate to SMURF Directory

```bash
cd dst-SRI_DST_BuildON-prod/smurf_web
```

### 2. Build and Start Services

```bash
docker-compose up --build -d
```

This command will:
- Build the SMURF Docker container
- Start Django application server
- Initialize PostgreSQL database
- Make the application available at [http://localhost:8080/smurf](http://localhost:8080/smurf)

### 3. Run Database Migrations (First Time Only)

```bash
docker-compose exec web python manage.py migrate
```

### 4. Load Technology Catalogue

```bash
docker-compose exec web python fill_models.py
```

This will populate the database with:
- Smart building equipment specifications
- Indicative costs per technology
- Technical characteristics (efficiency, power consumption, etc.)
- Environmental impact indicators

### 5. Stop Services

```bash
docker-compose down
```

## Manual Installation (Development)

### 1. Create Virtual Environment

```bash
cd dst-SRI_DST_BuildON-prod/smurf_web

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Database

Edit `smurf_web/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'smurf_db',
        'USER': 'admin',
        'PASSWORD': 'admin!',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Load Technology Catalogue

```bash
python fill_models.py
```

### 6. Start Development Server

```bash
python manage.py runserver 8080
```

Access SMURF at [http://localhost:8080/smurf](http://localhost:8080/smurf).

## Project Structure

```
dst-SRI_DST_BuildON-prod/
├── README.md                    # This file
├── data_SRI.json                # Sample SRI assessment data
├── output_sri_scenarios1.json   # Sample scenario output
│
└── smurf_web/                   # Django application root
    ├── manage.py                # Django management script
    ├── requirements.txt         # Python dependencies
    ├── fill_models.py           # Technology catalogue loader
    ├── fill_models_old.py       # Legacy loader (deprecated)
    │
    ├── config/                  # Docker configuration
    │   ├── docker-compose.yaml  # Container orchestration
    │   ├── Dockerfile           # Container definition
    │   └── run.sh               # Startup script
    │
    ├── smurf_web/               # Django project configuration
    │   ├── __init__.py
    │   ├── settings.py          # Application settings
    │   ├── urls.py              # URL routing
    │   ├── wsgi.py              # WSGI entry point
    │   └── asgi.py              # ASGI entry point
    │
    ├── smurf_web_app/           # Main application module
    │   ├── __init__.py
    │   ├── admin.py             # Django admin configuration
    │   ├── models.py            # Database models
    │   ├── views.py             # Request handlers
    │   ├── urls.py              # App-level URL routing
    │   ├── forms.py             # Django forms
    │   ├── scenarios.py         # Scenario generation engine
    │   ├── csvhandle.py         # CSV data import utilities
    │   ├── singularhandle.py    # Single-building scenario logic
    │   └── static/              # Static assets (CSS, JS, images)
    │
    ├── templates/               # HTML templates
    │   ├── base.html            # Base template
    │   ├── landing_page.html    # Home page
    │   ├── set_sri_goal.html    # Target setting interface
    │   ├── upgrade_scenarios.html  # Scenario comparison view
    │   ├── about.html           # About page
    │   ├── 404.html             # Error pages
    │   └── 500.html
    │
    ├── excel_files/             # Equipment catalogue data
    │   ├── domain_w.csv         # Domain weights
    │   ├── impact_w.csv         # Impact criteria weights
    │   ├── services.csv         # Smart-ready services
    │   ├── levels.csv           # Functionality level definitions
    │   ├── costtechs.csv        # Technology costs (original)
    │   ├── costtechsnew.csv     # Updated cost data
    │   ├── costtechsnew2.csv    # Version 2
    │   ├── costtechsnew3.csv    # Version 3 (latest)
    │   └── IT Table_*.csv       # IT system specifications
    │
    └── static/                  # Collected static files (Django collectstatic)
        ├── admin/               # Django admin static files
        └── smurf_web_app/       # Application static files
```

## Configuration

### Environment Variables

Create a `.env` file or configure in `smurf_web/settings.py`:

```python
# Database settings
DATABASE_NAME=smurf_db
DATABASE_USER=admin
DATABASE_PASSWORD=admin!
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Django settings
SECRET_KEY=your-secret-key-here
DEBUG=False  # Set to True for development
ALLOWED_HOSTS=localhost,127.0.0.1

# SRI Calculator integration
SRI_CALCULATOR_API_URL=http://localhost:8000
```

### Technology Catalogue Updates

To update the equipment catalogue:

1. Edit CSV files in `excel_files/`:
   - `costtechsnew3.csv` – Equipment costs and specifications
   - `services.csv` – Service definitions
   - `levels.csv` – Functionality levels

2. Reload data:
   ```bash
   python fill_models.py
   ```

## Usage Workflow

### 1. Import Baseline SRI Assessment

SMURF retrieves baseline assessment data from SRI Calculator via:

- Manual data upload (JSON format)
- Direct API integration (if both tools are running)

### 2. Set Target SRI Score

Define desired SRI improvement:
- Target overall SRI score (0-100%)
- Optional domain-specific targets
- Budget constraints (optional)

### 3. Generate Scenarios

SMURF automatically:
- Identifies services with upgrade potential
- Evaluates functionality-level improvements
- Maps upgrades to catalogue equipment
- Calculates costs and SRI impact
- Ranks scenarios by optimization criteria

### 4. Compare Scenarios

View ranked scenarios with:

**Ranking Criteria:**
- **SRI Gain** – Highest improvement first
- **Total Cost** – Lowest cost first
- **Cost-Effectiveness** – Best SRI gain per € invested

**Scenario Details:**
- Service-level changes (from level X to level Y)
- Recommended equipment and manufacturers
- Estimated investment cost
- Expected SRI increase
- Environmental impact (CO₂, energy consumption)

### 5. Export Results

Download scenario reports in:
- JSON format (machine-readable)
- PDF summary (planned feature)

## Scenario Generation Algorithm

### Step 1: Gap Analysis

Identify gaps between baseline and target SRI by:
- Comparing current vs. maximum functionality levels per service
- Calculating required SRI increase per domain
- Prioritizing high-impact services

### Step 2: Technology Matching

For each upgrade opportunity:
- Query technology catalogue for compatible equipment
- Filter by service type and functionality level support
- Retrieve cost and technical specifications

### Step 3: Scenario Composition

Generate alternative scenarios:
- Single-service upgrades
- Multi-service combinations
- Domain-focused strategies
- Budget-constrained options

### Step 4: Impact Calculation

For each scenario compute:
- Post-upgrade SRI score (overall, domain, impact criteria)
- Total investment cost
- Cost-effectiveness ratio
- Environmental indicators

### Step 5: Ranking and Presentation

Sort scenarios and display top recommendations with visualizations.

## API Endpoints (Internal)

SMURF exposes internal endpoints for:

- `POST /smurf/upload` – Upload baseline SRI data
- `POST /smurf/set_target` – Define target SRI score
- `POST /smurf/generate` – Trigger scenario generation
- `GET /smurf/scenarios/{id}` – Retrieve scenario details

## Integration with SRI Calculator

### Data Exchange Format

SMURF expects JSON input with:

```json
{
  "building_id": 123,
  "overall_sri": 45.2,
  "domains": {
    "heating": 50.0,
    "cooling": 40.0,
    "lighting": 60.0
  },
  "services": [
    {
      "service_id": "H1",
      "domain": "heating",
      "functionality_level": 1,
      "share": 100
    }
  ],
  "impact_criteria": {
    "energy_efficiency": 48.5,
    "comfort": 42.0
  }
}
```

### API Call Example

```python
import requests

# Fetch baseline assessment from SRI Calculator
response = requests.get(
    "http://localhost:8000/assessments/123/export"
)

baseline_data = response.json()

# Send to SMURF
smurf_response = requests.post(
    "http://localhost:8080/smurf/upload",
    json=baseline_data
)
```

## Technology Catalogue Schema

### Equipment Table Structure

| Field | Description | Example |
|-------|-------------|---------|
| `id` | Unique equipment identifier | `TECH_001` |
| `service_id` | Associated smart-ready service | `H1` (weather prediction) |
| `functionality_level` | Supported functionality level | `3` |
| `equipment_name` | Commercial product name | "Smart Thermostat Model X" |
| `manufacturer` | Equipment manufacturer | "Company ABC" |
| `cost_eur` | Indicative cost (€) | `450.00` |
| `installation_cost_eur` | Installation cost (€) | `200.00` |
| `power_consumption_w` | Rated power (W) | `5` |
| `efficiency_class` | Energy efficiency label | `A++` |
| `co2_kg_year` | Annual CO₂ emissions (kg) | `2.5` |
| `lifespan_years` | Expected lifespan | `15` |

### Adding New Equipment

1. Edit `excel_files/costtechsnew3.csv`
2. Add row with all required fields
3. Run `python fill_models.py`
4. Verify in database or SMURF admin panel

## Troubleshooting

### Port Conflict (8080 in use)

Edit `docker-compose.yaml`:

```yaml
ports:
  - "8081:8080"  # Use port 8081 instead
```

### Database Connection Errors

```bash
# Check database status
docker-compose ps

# View logs
docker-compose logs web

# Reset database
docker-compose down -v
docker-compose up --build
```

### Missing Technology Catalogue Data

```bash
# Reload catalogue
docker-compose exec web python fill_models.py

# Check if data exists
docker-compose exec web python manage.py shell
>>> from smurf_web_app.models import CostTech
>>> CostTech.objects.count()
```

### Scenario Generation Not Working

Verify:
- Baseline SRI data is correctly imported
- Target SRI score is higher than baseline
- Technology catalogue is populated

```bash
# Debug mode
docker-compose exec web python manage.py runserver 8080 --settings=smurf_web.settings --verbosity=3
```

## Testing

### Run Django Tests

```bash
python manage.py test smurf_web_app
```

### Manual Testing Checklist

- [ ] Upload baseline SRI data
- [ ] Set target SRI score
- [ ] Generate scenarios successfully
- [ ] View scenario comparison dashboard
- [ ] Verify cost calculations
- [ ] Check SRI score projections
- [ ] Validate equipment recommendations


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
