# FACULTY Q — Smart Faculty Scheduling and Reminder System

Full-stack academic management platform: Admin, Faculty, and Student dashboards.

## Tech Stack
- **Backend:** Python 3.12, FastAPI, SQLAlchemy, PostgreSQL, JWT
- **Frontend:** Flutter (web + mobile)
- **Database:** PostgreSQL 16
- **Cache/Queue:** Redis 7
- **Deployment:** Docker Compose

## Quick Start (Windows)

### 1. Start backend + database
```bash
cd D:\FacultyQ
docker compose up -d
```

### 2. Seed database
```bash
cd backend
pip install -r requirements.txt
python seed.py
```

### 3. Run backend locally (without Docker)
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 4. Run Flutter frontend
```bash
cd frontend
flutter pub get
flutter run -d chrome          # web
flutter run -d <device_id>     # mobile
```

## Demo Credentials
| Role | Email | Password |
|---|---|---|
| Admin | admin@facultyq.com | admin123 |
| Faculty | faculty1@facultyq.com | faculty123 |
| Student | student1@facultyq.com | student123 |

## API Docs
Open http://localhost:8000/docs after starting the backend.

## Phase 1 (Foundation) — Complete
- JWT auth with 3 roles (admin/faculty/student)
- All 22 DB tables with proper relationships
- Admin: create faculty/student, dashboard stats
- Faculty: today's timetable view
- Student: today's timetable view
- Notification preferences + unread count
- Assignments: CRUD + student view
- Substitutions: available faculty lookup, create, approve/reject
- Docker Compose (Postgres + Redis + backend)
- Seed data with demo accounts

## Next Phases
- Phase 2: Timetable upload (CSV/Excel), versioning, conflict detection
- Phase 3: 5-min class reminders (APScheduler), faculty availability, substitutions
- Phase 4: Assignments/projects with deadline reminders (24h/12h/1h)
- Phase 5: Full dashboards, notification service, email, tests, deployment