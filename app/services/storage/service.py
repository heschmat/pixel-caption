import shutil
import uuid
from pathlib import Path


class StorageError(Exception):
    pass


class LocalStorageService:
    def __init__(self, *, base_dir: str, bucket: str) -> None:
        self.base_dir = Path(base_dir)
        self.bucket = bucket

    def ensure_base_dir(self) -> None:
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def build_storage_key(self, filename: str) -> str:
        sanitized = filename.replace("/", "_").replace("\\", "_")
        return f"uploads/{uuid.uuid4()}-{sanitized}"

    def store_file(self, *, file_obj, storage_key: str) -> tuple[str, str]:
        self.ensure_base_dir()

        absolute_path = self.base_dir / storage_key
        absolute_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with absolute_path.open("wb") as buffer:
                shutil.copyfileobj(file_obj, buffer)
        except Exception as exc:
            raise StorageError(f"Failed to store file: {exc}") from exc

        storage_uri = f"file://{absolute_path}"
        return str(absolute_path), storage_uri

    def delete_file(self, *, storage_key: str) -> None:
        absolute_path = self.base_dir / storage_key
        if absolute_path.exists():
            absolute_path.unlink()

    def get_download_url(self, *, storage_key: str) -> str:
        absolute_path = self.base_dir / storage_key
        return f"file://{absolute_path}"
