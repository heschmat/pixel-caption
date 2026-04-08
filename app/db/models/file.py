from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class FileObject(TimestampMixin, Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)

    storage_provider: Mapped[str] = mapped_column(String(50), nullable=False, default="s3")
    storage_bucket: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(1024), unique=True, nullable=False)
    storage_uri: Mapped[str] = mapped_column(String(1200), unique=True, nullable=False)

    caption: Mapped[str | None] = mapped_column(String, nullable=True)
    caption_status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    caption_error: Mapped[str | None] = mapped_column(String, nullable=True)

    caption_style: Mapped[str | None] = mapped_column(String(50), nullable=True)
    caption_model: Mapped[str | None] = mapped_column(String(100), nullable=True)

    owner = relationship("User", back_populates="files")
