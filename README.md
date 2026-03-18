# 🎵 Music Player — Backend

A clean, minimal REST API built with **FastAPI** + **PostgreSQL** for uploading and streaming audio files.

---

## 📂 Project Structure

```
music-player/
├── backend/
│   ├── main.py          # FastAPI app — routes and startup logic
│   ├── models.py        # SQLAlchemy ORM models
│   ├── database.py      # DB engine, session factory
│   ├── schemas.py       # Pydantic request/response schemas
│   ├── auth.py          # HTTP Basic Auth with bcrypt
│   ├── config.py        # Centralized settings (reads .env)
│   ├── requirements.txt
│   └── .env.example     # Copy to .env and fill in your values
└── media/               # Uploaded audio files are stored here
```

---

## ⚙️ Prerequisites

- Python 3.11+
- PostgreSQL running locally (or via Docker)

---

## 🚀 Setup & Run

### 1. Start PostgreSQL

**Option A — Local install:**
```bash
# macOS (Homebrew)
brew services start postgresql

# Ubuntu/Debian
sudo service postgresql start
```

**Option B — Docker (recommended):**
```bash
docker run -d \
  --name music-player-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=music_player \
  -p 5432:5432 \
  postgres:16
```

---

### 2. Configure Environment

```bash
cd backend
cp .env.example .env
# Edit .env if you need different credentials or DB URL
```

---

### 3. Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

### 4. Start the FastAPI Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: **http://localhost:8000**

> Database tables are created automatically on first startup.

---

## 📖 API Reference

All endpoints (except `/health`) require **HTTP Basic Auth**.

Default credentials (from `.env`):
- Username: `admin`
- Password: `changeme`

| Method | Endpoint           | Description                        |
|--------|--------------------|------------------------------------|
| GET    | `/health`          | Health check (no auth)             |
| POST   | `/upload`          | Upload an mp3 or wav file          |
| GET    | `/songs`           | List all uploaded songs            |
| GET    | `/songs/{id}/play` | Stream audio for a specific song   |

### Interactive Docs

FastAPI auto-generates interactive documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔐 Authentication

Uses **HTTP Basic Auth** — send `Authorization: Basic <base64(user:pass)>` header with every request.

In `curl`:
```bash
curl -u admin:changeme http://localhost:8000/songs
```

Passwords are hashed with **bcrypt** at startup. Change `AUTH_PASSWORD` in `.env` for production.

---

## 🧪 Testing the API

```bash
# Health check
curl http://localhost:8000/health

# Upload a song
curl -u admin:changeme \
  -X POST http://localhost:8000/upload \
  -F "file=@/path/to/song.mp3"

# List songs
curl -u admin:changeme http://localhost:8000/songs

# Stream song with id=1
curl -u admin:changeme http://localhost:8000/songs/1/play --output test.mp3
```

---

## 🎵 Supported Formats

| Format | MIME Type   |
|--------|-------------|
| `.mp3` | audio/mpeg  |
| `.wav` | audio/wav   |

---

## 🏗️ Design Decisions

| Decision | Reason |
|---|---|
| Basic Auth (no JWT) | Simplicity — single user, no token rotation needed |
| bcrypt password hashing | Industry standard, protects password at rest |
| `StreamingResponse` for audio | Avoids loading entire file into memory |
| Pydantic settings (`config.py`) | Centralized config, easy to override via env |
| Separate schemas from models | Clean separation of DB layer and API layer |
| `_unique_path()` helper | Prevents silent overwrites on duplicate uploads |
