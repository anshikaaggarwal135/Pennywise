# Pennywise — Personal Expense Tracker

A modern full-stack rebuild of the earlier Flask/SQLite ExpenseTracker. The original project stored income and expenses in a single local SQLite table and rendered a Flask dashboard. This version preserves the core transaction workflow while adding per-user accounts, protected APIs, monthly analytics and budgets, using the newer stack specified in the project PDF.

## Features
- Account registration, login, logout and protected JWT API routes
- Password hashing; users can only access their own transactions and budgets
- Create, view, edit and delete income/expense transactions
- Categories, text search, type/category filters and sorting
- Monthly income, expense, balance and savings-rate summary
- Six-month expense trend and category-wise doughnut chart
- Monthly category/overall budgets with progress and over-budget warning
- Responsive dark finance dashboard
- PostgreSQL + SQLAlchemy + Alembic migrations
- Dockerfile, Docker Compose, Render and Vercel deployment configuration
- API docs at `/docs`; health endpoint at `/health`

## Project structure
```text
PersonalExpenseTracker/
├── backend/
│   ├── app/ (api, core, db, models, schemas)
│   ├── alembic/versions/ (database migrations)
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/ (components, context, lib, pages)
│   ├── package.json
│   └── vercel.json
├── docker-compose.yml
└── render.yaml
```

## Run locally on Windows (PowerShell)
### 1. Backend — quick local mode (SQLite)
```powershell
cd backend
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Keep DATABASE_URL=sqlite:///./expense_tracker.db in .env for this mode
alembic upgrade head
uvicorn app.main:app --reload
```
API: http://127.0.0.1:8000 | Swagger: http://127.0.0.1:8000/docs

### 2. Frontend
Open a second terminal:
```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```
Open http://localhost:5173. Register an account, then add transactions.

### Import your earlier project data (optional)
The original uploaded SQLite database is included at `backend/legacy_data/legacy_expenses.db`. After registering your account and starting the backend at least once, open a backend terminal and run:
```powershell
python scripts/import_legacy_sqlite.py your-email@example.com
```
The script imports the six transactions from the previous Flask project into that account and skips duplicates if you run it again.

## Run with PostgreSQL using Docker
From the project root (Docker Desktop must be running):
```powershell
docker compose up --build
```
This starts PostgreSQL and the FastAPI container. Alembic migrations are applied at container startup. Then run the React frontend separately:
```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

## Database migrations
Run from `backend/` with the virtual environment active and `DATABASE_URL` configured:
```powershell
alembic upgrade head
alembic revision --autogenerate -m "describe your change"
alembic upgrade head
```
The app schema is managed by Alembic. Apply migrations before starting the API; the Docker/production startup does this automatically.

## Tests
From `backend/`:
```powershell
pip install -r requirements.txt
pytest -q
```

## Deployment
### Backend — Render
1. Push this project to GitHub.
2. Create a managed PostgreSQL database on Render and copy its internal connection URL.
3. Create a Web Service from the repository using the included `render.yaml` / Dockerfile.
4. Set `DATABASE_URL` to the Render PostgreSQL URL (SQLAlchemy driver form `postgresql+psycopg://...`), `SECRET_KEY` to a long random value, and `CORS_ORIGINS` to the deployed Vercel URL.
5. Deploy. Verify `/health` and `/docs`.

### Frontend — Vercel
1. Import the repository into Vercel and set the Root Directory to `frontend`.
2. Framework: Vite; build command `npm run build`; output directory `dist`.
3. Add `VITE_API_URL=https://YOUR-RENDER-SERVICE.onrender.com/api`.
4. Deploy. The included `vercel.json` supports React Router refreshes.
5. Update the backend `CORS_ORIGINS` with the final Vercel domain and redeploy the backend.

## Important security notes
- Never commit `.env` files or production secrets.
- Replace the development secret before deployment.
- Use HTTPS in production and restrict CORS to the exact frontend origin.
- The included local SQLite fallback is for development; PostgreSQL is the recommended production database.

## Existing project reuse
The previous ExpenseTracker contained a Flask app, SQLite transaction storage, dashboard, transaction templates, CSS and Chart.js. Its original six SQLite transactions are included with an import script so you can carry them into your new account. The new app carries forward its income/expense model, transaction CRUD, category-based summaries and chart-driven dashboard, but replaces the server-rendered Flask/SQLite architecture with the FastAPI + React architecture in the PDF's later technology section.
