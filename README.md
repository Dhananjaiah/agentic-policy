##############################
# 0. Create project skeleton
##############################
mkdir -p /home/jai/Desktop/agentic-insurance-bot
cd /home/jai/Desktop/agentic-insurance-bot
git init

mkdir backend infra docs

##############################
# 1. Backend Python env
##############################
cd backend
python -m venv .venv
source .venv/bin/activate

# Core backend + env libs
pip install fastapi uvicorn[standard] python-dotenv

# DB + AI + agent stack
pip install psycopg2-binary Faker \
           langchain langchain-openai langgraph langchain-core

##############################
# 2. Postgres (Docker) + schema
##############################
cd /home/jai/Desktop/agentic-insurance-bot
mkdir -p infra/sql
cd infra

# Start Postgres with our schema (init_core_schema.sql already created)
docker compose -f docker-compose.db.yml up -d

# Optional: check DB tables from inside container
docker exec -it insurance-postgres \
  psql -U insurance_user -d insurance_core -c "\dt"

##############################
# 3. Seed realistic data
##############################
cd /home/jai/Desktop/agentic-insurance-bot/backend
source .venv/bin/activate

# (Already installed Faker + psycopg2 above)
# Make sure .env.local has DB_* vars

python seed_data.py

##############################
# 4. Set OpenAI key (if not using .env.local load)
##############################
cd /home/jai/Desktop/agentic-insurance-bot/backend
source .venv/bin/activate

export OPENAI_API_KEY="sk-your-real-key-here"

##############################
# 5. Run backend API (FastAPI + agent)
##############################
cd /home/jai/Desktop/agentic-insurance-bot
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

##############################
# 6. Test endpoints
##############################
# Health check
curl http://localhost:8000/health

# Agent call (use a valid CLM-2xxxxx from seeded data)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"userId":"U123","message":"What is the status of claim CLM-200000?"}'

