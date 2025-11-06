# Jewelry Shop Task Manager - Backend

FastAPI backend for the jewelry shop task management system.

## Setup

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env and fill in your values
```

### 4. Set Up Database

Make sure PostgreSQL is running and create the database:

```bash
createdb jewelry_tasks
```

### 5. Run Database Migrations

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 6. Run the Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

## Project Structure

```
backend/
├── app/
│   ├── api/          # API route handlers
│   ├── models/       # SQLAlchemy models
│   ├── schemas/      # Pydantic schemas
│   ├── core/         # Core configuration
│   ├── services/     # Business logic services
│   └── main.py       # FastAPI application
├── alembic/          # Database migrations
├── tests/            # Test files
└── requirements.txt  # Python dependencies
```

## Development

### Create a New Migration

```bash
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

### Run Tests

```bash
pytest
```

### Code Formatting

```bash
black app/
```
