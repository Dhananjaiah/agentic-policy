FROM python:3.11-slim

WORKDIR /app

# System deps for psycopg2
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy requirements from backend folder (build context = project root)
COPY backend/requirements.txt ./requirements.txt

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code into the image
COPY backend ./backend

# Expose FastAPI port
EXPOSE 8000

# Run the FastAPI app
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

