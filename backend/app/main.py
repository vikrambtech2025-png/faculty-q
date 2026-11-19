from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.database import engine, Base
from app.routers import auth, admin, timetable, substitution, assignment, notification, dashboard
from app.services.scheduler import start_scheduler, stop_scheduler

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    stop_scheduler()

app = FastAPI(title="FACULTY Q API", version="1.0.0", docs_url="/docs", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(timetable.router)
app.include_router(substitution.router)
app.include_router(assignment.router)
app.include_router(notification.router)
app.include_router(dashboard.router)

@app.get("/")
def root():
    return {"app": "FACULTY Q", "status": "running", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}