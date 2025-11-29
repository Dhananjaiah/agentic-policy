################################################################################
# 0. PROJECT ROOT
################################################################################
cd /home/jai/Desktop/agentic-insurance-bot

################################################################################
# 1. ONE-TIME BACKEND SETUP (PYTHON VENV + DEPS)
################################################################################
cd backend

# Create virtual env
python -m venv .venv

# Activate venv
# Linux / macOS:
source .venv/bin/activate
# Windows (PowerShell):
# .venv\Scripts\Activate.ps1

# Install backend dependencies
pip install -r requirements.txt

# Create local env file for host-side dev (WITHOUT committing it)
# (Just create the file; fill values manually in your editor)
touch .env.local

# .env.local should contain DB connection + LLM key, for example:
#   DB_HOST=localhost
#   DB_PORT=5432
#   DB_NAME=insurance_core
#   DB_USER=insurance_user
#   DB_PASSWORD=insurance_pass
#   OPENAI_API_KEY=...         # <- set locally, DO NOT COMMIT
#
# Do NOT paste example keys or real keys into README or git.

cd ..

################################################################################
# 2. DOCKER COMPOSE MODE (DB + API TOGETHER)
################################################################################
cd infra

# IMPORTANT:
# Before running this, make sure your shell has the LLM key exported
# in the variable name expected by the backend (e.g. OPENAI_API_KEY),
# but do that outside of this README and NEVER commit that command.

# Start BOTH services:
#   - postgres  (DB)
#   - api       (FastAPI + Uvicorn + agent backend)
docker compose -f docker-compose.local.yml up --build

# Leave this terminal running (it is your DB + API stack)

################################################################################
# 3. SEED THE DATABASE (RUN ON HOST, ONCE PER FRESH DB)
################################################################################
# Open a NEW terminal window
cd /home/jai/Desktop/agentic-insurance-bot/backend

# Activate venv again
source .venv/bin/activate

# Make sure .env.local has valid DB_* settings for localhost:5432
python seed_data.py

# Optional: verify row counts directly in DB container
docker exec -it insurance-postgres \
  psql -U insurance_user -d insurance_core -c "SELECT count(*) FROM claims;"

################################################################################
# 4. CHECK API (RUNNING IN DOCKER)
################################################################################
# From any terminal on host:
curl http://localhost:8000/health

# Simple agent test (use a valid CLM-2xxxxx if needed)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"userId":"demo-user","message":"What is the status of claim CLM-200000?"}'

################################################################################
# 5. FRONTEND – SIMPLE SEARCH BOX UI
################################################################################
cd /home/jai/Desktop/agentic-insurance-bot/frontend

# Static file server for index.html
python -m http.server 5500

# Open in browser:
#   http://localhost:5500/index.html
#
# This page:
#   - shows a search box
#   - calls POST http://localhost:8000/chat
#   - displays the agent's answer

################################################################################
# 6. OPTIONAL: DEV MODE WITHOUT DOCKER (API ONLY)
################################################################################
# If you want to run ONLY the API locally, without containerizing it:

# 6.1 Stop docker-compose services (if running)
cd /home/jai/Desktop/agentic-insurance-bot/infra
docker compose -f docker-compose.local.yml down

# 6.2 Start ONLY Postgres with docker-compose (optional)
docker compose -f docker-compose.local.yml up postgres

# 6.3 Run API directly with uvicorn (in another terminal)
cd /home/jai/Desktop/agentic-insurance-bot/backend
source .venv/bin/activate

# IMPORTANT: ensure your LLM provider key is set in your shell
# using the env var name expected by the code (e.g. OPENAI_API_KEY).
# Do this manually, not in README, and never commit that command.

uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Frontend stays the same:
#   cd frontend
#   python -m http.server 5500
#   open http://localhost:5500/index.html

################################################################################
# 7. CLEAN UP
################################################################################
# Stop all containers
cd /home/jai/Desktop/agentic-insurance-bot/infra
docker compose -f docker-compose.local.yml down

# Deactivate venv
cd /home/jai/Desktop/agentic-insurance-bot/backend
deactivate  # or just close the terminal

