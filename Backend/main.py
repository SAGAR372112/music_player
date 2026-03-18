"""
main.py
-------
FastAPI application entry point.

Routes:
    POST /upload          — Upload an audio file (mp3 or wav)
    GET  /songs           — List all uploaded songs
    GET  /songs/{id}/play — Stream audio for a specific song
    GET  /health          — Health check (no auth required)
"""

import os
import urllib.parse
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from config import settings
from database import Base, engine, get_db
from models import Song
from schemas import SongCreate, SongResponse, UploadResponse

# ---------------------------------------------------------------------------
# App Initialization
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    description="A simple music player backend — upload and stream audio files.",
)

# Allow Streamlit (or any frontend) to call this API from a different origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Startup: create tables and ensure media directory exists
# ---------------------------------------------------------------------------

MEDIA_DIR = Path(settings.MEDIA_DIR)
ALLOWED_EXTENSIONS = {".mp3", ".wav"}
CHUNK_SIZE = 1024 * 1024  # 1 MB — chunk size for audio streaming


@app.on_event("startup")
def on_startup():
    """Create DB tables and media directory on first run."""
    Base.metadata.create_all(bind=engine)
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------------

@app.get("/health", tags=["Health"])
def health_check():
    """Simple health check — no authentication required."""
    return {"status": "ok", "version": settings.APP_VERSION}


# ---------------------------------------------------------------------------
# POST /upload — Upload a song
# ---------------------------------------------------------------------------

@app.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Songs"],
    summary="Upload an audio file (mp3 or wav)",
)
async def upload_song(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload an audio file and store its metadata in the database.

    - Accepts: mp3, wav
    - Saves the file to the configured MEDIA_DIR
    - Returns the created song record
    """
    # --- Validate file extension ---
    original_name = file.filename or "unknown"
    ext = Path(original_name).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # --- Sanitize filename and build save path ---
    safe_name = _sanitize_filename(original_name)
    save_path = MEDIA_DIR / safe_name

    # Avoid overwriting existing files by appending a counter
    save_path = _unique_path(save_path)

    # --- Write file to disk ---
    try:
        contents = await file.read()
        save_path.write_bytes(contents)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {exc}",
        )

    # --- Persist metadata to DB ---
    song_data = SongCreate(
        title=save_path.stem,           # Use filename (without extension) as title
        file_path=str(save_path),
    )
    song = Song(**song_data.model_dump())
    db.add(song)
    db.commit()
    db.refresh(song)

    return UploadResponse(
        message="Song uploaded successfully.",
        song=SongResponse.model_validate(song),
    )


# ---------------------------------------------------------------------------
# GET /songs — List all songs
# ---------------------------------------------------------------------------

@app.get(
    "/songs",
    response_model=list[SongResponse],
    tags=["Songs"],
    summary="List all uploaded songs",
)
def list_songs(
    db: Session = Depends(get_db)
):
    """Return all songs from the database, ordered by upload date (newest first)."""
    songs = db.query(Song).order_by(Song.uploaded_at.desc()).all()
    return [SongResponse.model_validate(s) for s in songs]


# ---------------------------------------------------------------------------
# GET /songs/{id}/play — Stream a song
# ---------------------------------------------------------------------------

@app.get(
    "/songs/{song_id}/play",
    tags=["Songs"],
    summary="Stream audio for a specific song",
    responses={
        200: {"content": {"audio/mpeg": {}, "audio/wav": {}}},
        404: {"description": "Song not found"},
    },
)
def play_song(
    song_id: int,
    db: Session = Depends(get_db),
):
    """
    Stream the audio file for the given song ID.

    Uses StreamingResponse with chunked file reading to handle large files
    without loading the entire file into memory.
    """
    # --- Fetch song from DB ---
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song with id={song_id} not found.",
        )

    # --- Check file exists on disk ---
    file_path = Path(song.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio file not found on disk.",
        )

    # --- Determine MIME type ---
    media_type = _get_media_type(file_path.suffix.lower())

    # --- Stream file in chunks ---
    def iter_file():
        with open(file_path, "rb") as f:
            while chunk := f.read(CHUNK_SIZE):
                yield chunk

    return StreamingResponse(
        iter_file(),
        media_type=media_type,
        headers={
            "Content-Disposition": f'inline; filename="{urllib.parse.quote(file_path.name)}"',
            "Content-Length": str(file_path.stat().st_size),
            "Accept-Ranges": "bytes",
        },
    )


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

def _sanitize_filename(filename: str) -> str:
    """Remove path separators and whitespace from a filename."""
    name = os.path.basename(filename)          # Strip any directory components
    name = name.replace(" ", "_")              # Replace spaces with underscores
    return name


def _unique_path(path: Path) -> Path:
    """
    If the given path already exists, append an incrementing counter
    to the stem until a unique path is found.

    Example: song.mp3 → song_1.mp3 → song_2.mp3
    """
    if not path.exists():
        return path

    counter = 1
    while True:
        new_path = path.with_stem(f"{path.stem}_{counter}")
        if not new_path.exists():
            return new_path
        counter += 1


def _get_media_type(extension: str) -> str:
    """Map a file extension to its MIME type."""
    mime_map = {
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
    }
    return mime_map.get(extension, "application/octet-stream")
