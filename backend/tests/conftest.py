import pytest, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["DATABASE_URL"] = "sqlite:///./test_facultyq.db"
from app.core.database import engine, Base, SessionLocal
from app.main import app
from fastapi.testclient import TestClient

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    # Seed data
    seed_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "seed.py")
    with open(seed_path) as f:
        code = compile(f.read(), seed_path, "exec")
    # Redirect DB to test db (already set via env)
    exec(code, {"__name__": "__seed__", "__file__": seed_path})
    yield
    Base.metadata.drop_all(bind=engine)
    import time
    for _ in range(5):
        try:
            if os.path.exists("test_facultyq.db"):
                os.remove("test_facultyq.db")
            break
        except PermissionError:
            time.sleep(0.5)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def admin_token(client):
    r = client.post("/api/auth/login", json={"email": "admin@facultyq.com", "password": "admin123"})
    assert r.status_code == 200
    return r.json()["access_token"]

@pytest.fixture
def faculty_token(client):
    r = client.post("/api/auth/login", json={"email": "faculty1@facultyq.com", "password": "faculty123"})
    assert r.status_code == 200
    return r.json()["access_token"]

@pytest.fixture
def student_token(client):
    r = client.post("/api/auth/login", json={"email": "student1@facultyq.com", "password": "student123"})
    assert r.status_code == 200
    return r.json()["access_token"]