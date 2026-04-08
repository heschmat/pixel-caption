import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.db import get_db
from app.core.config import settings
from app.db.models.user import User
from app.repositories.files import (
    create_file,
    delete_file as delete_file_record,
    get_file_by_id,
    list_files_by_owner,
)
from app.schemas.file import FileDownloadResponse, FileRead
from app.services.storage.service import LocalStorageService, StorageError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/files", tags=["files"])


def _ensure_image(content_type: str | None) -> None:
    if not content_type or not content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image uploads are supported.",
        )


def get_storage_service() -> LocalStorageService:
    return LocalStorageService(
        base_dir=settings.storage_base_dir,
        bucket=settings.storage_bucket,
    )


@router.post("", response_model=FileRead, status_code=status.HTTP_201_CREATED)
def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FileRead:
    _ensure_image(file.content_type)

    storage_service = get_storage_service()
    storage_key = storage_service.build_storage_key(file.filename)

    file.file.seek(0, 2)
    size_bytes = file.file.tell()
    file.file.seek(0)

    try:
        absolute_path, storage_uri = storage_service.store_file(
            file_obj=file.file,
            storage_key=storage_key,
        )

        file_obj = create_file(
            db,
            owner_id=current_user.id,
            original_filename=file.filename,
            content_type=file.content_type,
            size_bytes=size_bytes,
            storage_provider=settings.storage_provider,
            storage_bucket=settings.storage_bucket,
            storage_key=storage_key,
            storage_uri=storage_uri,
        )

        logger.info(
            "file_uploaded",
            extra={
                "file_id": file_obj.id,
                "user_id": current_user.id,
                "storage_key": file_obj.storage_key,
                "absolute_path": absolute_path,
            },
        )

        return file_obj

    except StorageError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


@router.get("", response_model=list[FileRead])
def list_my_files(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[FileRead]:
    return list_files_by_owner(db, current_user.id)


@router.get("/{file_id}", response_model=FileRead)
def get_my_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FileRead:
    file_obj = get_file_by_id(db, file_id)
    if not file_obj or file_obj.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found.")
    return file_obj


@router.get("/{file_id}/download", response_model=FileDownloadResponse)
def get_download_url(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FileDownloadResponse:
    file_obj = get_file_by_id(db, file_id)
    if not file_obj or file_obj.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found.")

    storage_service = get_storage_service()
    download_url = storage_service.get_download_url(storage_key=file_obj.storage_key)
    return FileDownloadResponse(download_url=download_url)


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    file_obj = get_file_by_id(db, file_id)
    if not file_obj or file_obj.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found.")

    storage_service = get_storage_service()
    storage_service.delete_file(storage_key=file_obj.storage_key)
    delete_file_record(db, file_obj)

    logger.info(
        "file_deleted",
        extra={
            "file_id": file_id,
            "user_id": current_user.id,
            "storage_key": file_obj.storage_key,
        },
    )
