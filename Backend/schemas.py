"""
schemas.py
----------
Pydantic schemas for request validation and API response serialization.
These are separate from the ORM models to keep concerns clean.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SongBase(BaseModel):
    """Shared fields used across Song schemas."""
    title: str


class SongCreate(SongBase):
    """Schema used internally when saving a new song to the database."""
    file_path: str


class SongResponse(SongBase):
    """Schema returned to the client when listing or fetching songs."""
    id: int
    title: str
    file_path: str
    uploaded_at: datetime

    # Enable ORM mode so Pydantic can read from SQLAlchemy model instances
    model_config = ConfigDict(from_attributes=True)


class UploadResponse(BaseModel):
    """Response returned after a successful file upload."""
    message: str
    song: SongResponse


class ErrorResponse(BaseModel):
    """Standard error response shape."""
    detail: str
