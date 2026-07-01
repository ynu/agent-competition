# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

智能体大赛网站 (Agent Competition) - A full-stack competition management system for AI agent competitions.

- **Backend**: Python FastAPI + SQLAlchemy 2.0 (default SQLite, supports MySQL/PostgreSQL)
- **Frontend**: Vue 3 (Composition API) + Vite + TailwindCSS 4 + Pinia

## Commands

### Backend (cd backend)

```bash
# Install dependencies
uv pip install -e .

# Initialize database
uv run python init_db.py

# Start development server (http://localhost:8000)
uv run python main.py

# Run with uvicorn hot reload
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (cd frontend)

```bash
# Install dependencies
npm install

# Start dev server (http://localhost:5173)
npm run dev

# Build for production
npm run build

# Type check
npm run build  # runs vue-tsc -b
```

### Default Login
- Username: `admin`
- Password: `admin123`

## Architecture

### Backend Structure (`backend/`)
- `app/api/` - API route handlers (auth, users, teams, works, reviews, contents, settings, logs)
- `app/core/` - Core modules: config.py, database.py, security.py
- `app/models/` - SQLAlchemy ORM models
- `app/schemas/` - Pydantic request/response schemas

### Frontend Structure (`frontend/src/`)
- `pages/` - Route pages, admin pages under `pages/admin/`
- `stores/` - Pinia stores for state management
- `api/` - Axios API clients
- `components/` - Reusable Vue components
- `router/` - Vue Router configuration

### Key Patterns
- **Auth**: JWT tokens, SSO header support (X-Remote-User/Nickname/Email)
- **RBAC**: Three roles - user, reviewer, admin
- **File uploads**: Works accept PDF (≤10MB) and video (≤50MB), stored in `backend/uploads/`
- **Voting**: Configurable daily limit per user (default 5 votes/day)

### API Documentation
Interactive docs available at http://localhost:8000/docs (Swagger UI)

## Environment Configuration

Create `backend/.env` for custom settings:
```
DATABASE_URL=sqlite:///./agent_competition.db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```