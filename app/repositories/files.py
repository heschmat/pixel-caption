from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.file import FileObject


def create_file(
    db: Session,
    *,
    owner_id: int,
    original_filename: str,
    content_type: str | None,
    size_bytes: int,
    storage_provider: str,
    storage_bucket: str,
    storage_key: str,
    storage_uri: str,
) -> FileObject:
    file_obj = FileObject(
        owner_id=owner_id,
        original_filename=original_filename,
        content_type=content_type,
        size_bytes=size_bytes,
        storage_provider=storage_provider,
        storage_bucket=storage_bucket,
        storage_key=storage_key,
        storage_uri=storage_uri,
        caption_status="pending",
    )
    db.add(file_obj)
    db.commit()
    # Refresh the instance to get the generated ID and timestamps from the database
    db.refresh(file_obj)
    return file_obj


def get_file_by_id(db: Session, file_id: int) -> FileObject | None:
    return db.get(FileObject, file_id)


def list_files_by_owner(db: Session, owner_id: int) -> list[FileObject]:
    statement = (
        select(FileObject)
        .where(FileObject.owner_id == owner_id)
        .order_by(FileObject.created_at.desc())
    )
    return list(db.execute(statement).scalars().all())


def delete_file(db: Session, file_obj: FileObject) -> None:
    db.delete(file_obj)
    db.commit()
