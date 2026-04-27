# Quick Start Guide

Get up and running with BuildON SRI Tools in under 10 minutes.

## Prerequisites Check

Before starting, ensure you have:

- Docker installed (version 20.10+)  
  Check: `docker --version`
  
- Docker Compose installed (version 1.29+)  
  Check: `docker-compose --version`
  
- At least 4GB RAM available
  
- Ports available: 3000, 8000, 8080

If any prerequisite is missing, see [Installation Prerequisites](#installation-prerequisites) below.

---

## 5-Minute Setup

### Step 1: Clone Repository

```bash
git clone https://github.com/epu-ntua/BuildON-SRI-Tools.git
cd BuildON-SRI-Tools
```

### Step 2: Start SRI Calculator

```bash
cd SRI-calculator-main
docker network create sri-net
docker-compose up -d --build
```

Wait for services to start (~2-3 minutes for first build).

**Verify it's running:**
- Open [http://localhost:3000](http://localhost:3000) in your browser
- You should see the SRI Calculator landing page

### Step 3: Start SMURF

Open a new terminal window:

```bash
cd BuildON-SRI-Tools/dst-SRI_DST_BuildON-prod/smurf_web
docker-compose up -d --build
```

Wait for services to start (~1-2 minutes).

**Verify it's running:**
- Open [http://localhost:8080/smurf](http://localhost:8080/smurf)
- You should see the SMURF landing page

### Step 4: Initialize Database (First Time Only)

For SRI Calculator:
```bash
cd BuildON-SRI-Tools/SRI-calculator-main
docker-compose exec backend python db_init.py
```

For SMURF:
```bash
cd BuildON-SRI-Tools/dst-SRI_DST_BuildON-prod/smurf_web
docker-compose exec web python manage.py migrate
docker-compose exec web python fill_models.py
```

---

## Your First Assessment (10 Minutes)

### 1. Register Account

1. Navigate to [http://localhost:3000](http://localhost:3000)
2. Click "Register" 
3. Enter email and password
4. Login with your credentials

### 2. Create Building

1. Click "New Building"
2. Fill in basic information:
   - **Name**: "My Office Building"
   - **Location**: Your city
   - **Type**: Select "Office"
   - **Floor Area**: 1000 (m²)
   - **Construction Year**: 2010

### 3. Select Domains

Select which building systems are present:

- Heating
- Cooling  
- Lighting
- Electricity
- Domestic Hot Water (if not applicable)
- Ventilation (if not applicable)
- And so on...

### 4. Assign Service Levels

For each selected domain, you'll see smart-ready services.

**Example: Heating Domain**

Service: "Weather prediction controls" (H1)
- **Applicable?** Yes
- **Current Level:** 
  - Level 0: No controls
  - Level 1: Manual adjustment
  - **Level 2: Scheduled control** ← Select this
  - Level 3: Automated with weather forecast
  - Level 4: Advanced AI-based optimization
- **Coverage:** 100%

Repeat for all services in all domains.

### 5. View Results

After completing all services:

1. Click "Calculate SRI"
2. View your results dashboard:
   - **Overall SRI Score**: e.g., 45% (Class C)
   - **Domain Scores**: See which domains perform well/poorly
   - **Impact Criteria**: Energy efficiency, comfort, etc.
   - **Key Functionalities**: Energy performance, flexibility, user response

### 6. Generate Upgrade Scenarios (SMURF)

1. From SRI Calculator results, click "Export to SMURF"
2. Or navigate to [http://localhost:8080/smurf](http://localhost:8080/smurf)
3. Import your assessment
4. Set target SRI: **65%** (aiming for Class B)
5. Click "Generate Scenarios"
6. Review ranked upgrade options:
   - **Best SRI Gain**: Highest improvement
   - **Lowest Cost**: Cheapest option
   - **Best Value**: Best bang for buck

### 7. Compare Scenarios

Each scenario shows:
- Services to upgrade (e.g., H1: Level 2 → Level 3)
- Recommended equipment (e.g., "Smart Thermostat X by Company Y")
- Estimated cost (e.g., €5,200)
- Expected SRI after upgrade (e.g., 67%)
- Cost per SRI point gained (e.g., €236/point)
- Environmental impact

---

## Understanding Your Results

### SRI Score Interpretation

| Score Range | Class | Interpretation |
|-------------|-------|----------------|
| 0-20% | Class E | Basic/limited smartness |
| 21-40% | Class D | Below average |
| 41-60% | Class C | Average smartness |
| 61-80% | Class B | Good smartness |
| 81-100% | Class A | Excellent smartness |

### Domain Scores

Identify weak areas:
- **Low scores (<40%)**: Priority for improvement
- **Medium scores (40-60%)**: Moderate improvement potential
- **High scores (>60%)**: Already performing well

### Impact Criteria

Understand where your building excels or needs work:
- **Energy Efficiency**: How well does it save energy?
- **Comfort**: Occupant thermal and visual comfort
- **Convenience**: Ease of use and automation
- **Health & Wellbeing**: IAQ, lighting quality
- **Maintenance**: Fault detection, predictive maintenance
- **Information**: Feedback to occupants
- **Energy Flexibility**: Demand response, load shifting

---

## Common First-Time Issues

### Issue: "Port 3000 already in use"

**Solution:**
```bash
# Find what's using port 3000
lsof -i :3000

# Kill the process (replace PID)
kill -9 <PID>

# Or edit docker-compose.yml to use different port
```

### Issue: "Cannot connect to Docker daemon"

**Solution:**
```bash
# Start Docker Desktop (macOS/Windows)
# Or start Docker service (Linux)
sudo systemctl start docker
```

### Issue: "Frontend builds but shows blank page"

**Solution:**
```bash
# Clear browser cache
# Or try in incognito mode
# Or check browser console for errors (F12)
```

### Issue: "Cannot fetch assessment data in SMURF"

**Solution:**
- Verify SRI Calculator is running: `docker ps`
- Check network connectivity: Both should be on correct network
- Verify assessment was saved (check in SRI Calculator)

---

## Quick Reference: Command Cheat Sheet

### Start Services
```bash
# Start SRI Calculator
cd SRI-calculator-main && docker-compose up -d

# Start SMURF  
cd dst-SRI_DST_BuildON-prod/smurf_web && docker-compose up -d
```

### Stop Services
```bash
# Stop SRI Calculator
cd SRI-calculator-main && docker-compose down

# Stop SMURF
cd dst-SRI_DST_BuildON-prod/smurf_web && docker-compose down
```

### View Logs
```bash
# SRI Calculator logs
docker-compose logs -f backend    # Backend logs
docker-compose logs -f frontend   # Frontend logs

# SMURF logs
docker-compose logs -f web
```

### Restart Services
```bash
docker-compose restart
```

### Rebuild After Code Changes
```bash
docker-compose up -d --build
```

---

## Installation Prerequisites

### Installing Docker

**macOS:**
1. Download [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)
2. Install and start Docker Desktop

**Windows:**
1. Download [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
2. Install and start Docker Desktop
3. Ensure WSL2 is enabled

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

Log out and log back in for group changes to take effect.

### Verify Installation
```bash
docker --version         # Should show 20.10+
docker-compose --version # Should show 1.29+
docker ps                # Should run without errors
```


