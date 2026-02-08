# 🚚 Amigos — Advanced Decision-Making in Road Logistics

A research/demo repository for adaptive logistics, load matching, and route management. This project contains a **Python-dominant backend** with advanced analytics, ML predictions, and comprehensive monitoring, plus a Vite + React TypeScript frontend.

## Status
- 🚧 **Backend (production-ready):** Comprehensive Python API with AI agents, analytics, ML models, and monitoring in `api.py`, `agents/`, `core/`, and `utils/`. Local development ready.
- 🎨 **Frontend (prototype):** Vite + React + TypeScript app in the `frontend/` folder with interactive visualizations.
- ✅ **Tests:** Comprehensive unit tests under `tests/` (run with `pytest`).
- 🐍 **Python-Dominant:** ~70% Python, ~30% JavaScript/TypeScript
- ⚠️ **Not production-ready:** Security, auth, scaling, and monitoring are not fully implemented.

## Deployed demo
- 🚀 **Frontend (deployed):** https://amigos-advanced-decision-making-in.vercel.app/  
- 🔗 **Backend API (deployed):** https://amigos-advanced-decision-making-in-road.onrender.com


## Quickstart (Backend)
- Prereqs: Python 3.8+ (3.10+ recommended), `pip`.
- Install and run:

```powershell
python -m venv venv
# Windows PowerShell — activate
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Start the backend API (simple entrypoint)
python api.py
```

(For POSIX shells: `python -m venv venv && source venv/bin/activate`)

## Quickstart (Frontend)
- Prereqs: Node.js (16+), `npm` or `pnpm`.

```bash
cd frontend
npm install
npm run dev
```

Open the dev server printed by Vite (usually http://localhost:5173) and ensure the backend (`api.py`) is running to enable API calls.

## Run Tests
- From repository root (after activating the Python venv and installing requirements):

```bash
pip install -r requirements.txt
pytest -q
```

## Project layout (key files & folders)
- [api.py](api.py) — Backend API entrypoint with 27+ endpoints.
- [requirements.txt](requirements.txt) — Python dependencies.
- [frontend](frontend) — Vite + React TypeScript frontend app.
- [agents](agents) — Agent modules: `fleet_monitor.py`, `load_matcher.py`, `route_manager.py`.
- [core](core) — Core models and metrics: `models.py`, `metrics.py`.
- [config/settings.py](config/settings.py) — Configuration settings.
- [tests](tests) — Test suite (`test_fleet_monitor.py`, `test_new_modules.py`).
- [utils](utils) — Advanced utilities:
  - `simulator.py` — Fleet simulation
  - `osrm_client.py` — Routing integration
  - `llm_client.py` — AI/LLM integration
  - `analytics.py` — 📊 Fleet analytics & statistics
  - `ml_predictor.py` — 🤖 ML models (delivery time, demand forecast)
  - `database.py` — 💾 SQLAlchemy ORM & persistence
  - `report_generator.py` — 📈 Professional reports (JSON/CSV/HTML)
  - `cache_manager.py` — ⚡ Intelligent caching system
  - `notification_system.py` — 🔔 Alerts & notifications
  - `data_validator.py` — ✅ Data validation & sanitization

## New Features & Capabilities

### 📊 Advanced Analytics
- Fleet performance analysis with KPIs
- Statistical analysis tools (percentiles, outliers, trends)
- Profitability calculations
- Vehicle ROI tracking
- Top performer identification

### 🤖 Machine Learning
- Delivery time prediction using Random Forest
- Demand forecasting with Gradient Boosting
- Route optimization algorithms
- Predictive maintenance modeling
- Feature importance analysis

### 💾 Database & Persistence
- SQLite database with SQLAlchemy ORM
- Vehicle, Load, Trip, Event, and Maintenance tracking
- Historical data storage
- Query APIs for analytics

### 📈 Professional Reporting
- Executive summary reports
- Financial performance reports
- Vehicle performance dashboards
- Load analysis reports
- Multi-format export (JSON, CSV, HTML)

### ⚡ Performance Optimization
- Intelligent LRU cache with TTL
- Route caching
- API response caching
- Cache statistics and monitoring

### 🔔 Monitoring & Alerts
- Automated fleet health monitoring
- 10+ alert types (fuel, maintenance, delays)
- 4 severity levels
- Alert acknowledgment system
- Multiple notification channels

### ✅ Data Quality
- Comprehensive data validation
- Business rule checking
- Input sanitization
- Batch validation support

## Usage notes
- The frontend expects a running backend for live data; toggle or mock data in the UI if needed.
- Check `DEMO_GUIDE_AI.md`, `DEPLOYMENT_GUIDE.md`, and `COMPLETE_CODE_WALKTHROUGH.md` for demos and deployment tips.
- See [PYTHON_MODULES_GUIDE.md](PYTHON_MODULES_GUIDE.md) for detailed documentation on all Python modules.
- See [PYTHON_ENHANCEMENT_SUMMARY.md](PYTHON_ENHANCEMENT_SUMMARY.md) for a summary of recent enhancements.

## API Endpoints

### Core Fleet Management
- `POST /api/initialize` - Initialize system with vehicles and loads
- `GET /api/state` - Get current fleet state
- `POST /api/cycle` - Run monitoring cycle
- `GET /api/vehicles` - Get all vehicles
- `GET /api/loads` - Get all loads
- `GET /api/metrics` - Get fleet metrics
- `POST /api/match-loads` - Intelligent load matching
- `POST /api/manage-routes` - Adaptive route management
- `POST /api/simulate-movement` - Simulate truck movement

### Analytics & ML
- `GET /api/analytics/fleet-performance` - Comprehensive analytics
- `POST /api/analytics/profitability` - Profitability metrics
- `POST /api/ml/predict-delivery-time` - ML delivery time prediction

### Reports
- `GET /api/reports/executive-summary` - Executive summary
- `GET /api/reports/financial` - Financial performance report

### Monitoring & Alerts
- `GET /api/notifications/active` - Get active alerts
- `POST /api/notifications/acknowledge/{id}` - Acknowledge alert
- `POST /api/monitoring/check-fleet` - Run health checks

### Validation & Cache
- `POST /api/validation/vehicle` - Validate vehicle data
- `POST /api/validation/load` - Validate load data
- `GET /api/cache/statistics` - Cache performance stats
- `POST /api/cache/clear` - Clear cache

### Database
- `GET /api/database/statistics` - Database statistics

## Contributing
- Open issues for bugs or feature requests.
- Send pull requests against `main`. Keep changes small and focused.

## License
- No explicit license file in repository. Add a `LICENSE` before reuse.

---
