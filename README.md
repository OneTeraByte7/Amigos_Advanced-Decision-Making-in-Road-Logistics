
# 🚚 Amigos — Advanced Decision-Making in Road Logistics

A research/demo repository for adaptive logistics, load matching, and route management. This project contains a Python backend API, simulation and agent components, and a Vite + React TypeScript frontend.

## Status
- 🚧 **Backend (prototype):** Basic API and agents live in [api.py](api.py), `agents/`, and `core/`. Local development ready.
- 🎨 **Frontend (prototype):** Vite + React + TypeScript app in the `frontend/` folder with interactive visualizations.
- ✅ **Tests:** Unit tests under `tests/` (run with `pytest`).
- ⚠️ **Not production-ready:** Security, auth, scaling, and monitoring are not implemented.

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
- [api.py](api.py) — Backend API entrypoint.
- [requirements.txt](requirements.txt) — Python dependencies.
- [frontend](frontend) — Vite + React TypeScript frontend app.
- [agents](agents) — Agent modules: `fleet_monitor.py`, `load_matcher.py`, `route_manager.py`.
- [core](core) — Core models and metrics: `models.py`, `metrics.py`.
- [config/settings.py](config/settings.py) — Configuration settings.
- [tests](tests) — Test suite (`test_fleet_monitor.py`, etc.).
- [utils](utils) — helpers: `simulator.py`, `osrm_client.py`, `llm_client.py`.

## Usage notes
- The frontend expects a running backend for live data; toggle or mock data in the UI if needed.
- Check `DEMO_GUIDE_AI.md`, `DEPLOYMENT_GUIDE.md`, and `COMPLETE_CODE_WALKTHROUGH.md` for demos and deployment tips.

## Contributing
- Open issues for bugs or feature requests.
- Send pull requests against `main`. Keep changes small and focused.

## License
- No explicit license file in repository. Add a `LICENSE` before reuse.

---

If you'd like, I can:
- 🔁 Update the deployed URLs with the real endpoints you provide.
- 🧪 Run the test suite now.
- 🐳 Add a `docker-compose.yml` or `Procfile` for easy local deployment.

