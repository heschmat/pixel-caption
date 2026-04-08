from datetime import datetime

from pydantic import BaseModel


class FileRead(BaseModel):
    id: int
    owner_id: int
    original_filename: str
    content_type: str | None
    size_bytes: int

    storage_provider: str
    storage_bucket: str
    storage_key: str
    storage_uri: str

    caption: str | None
    caption_status: str
    caption_error: str | None
    caption_style: str | None
    caption_model: str | None

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FileDownloadResponse(BaseModel):
    download_url: str
