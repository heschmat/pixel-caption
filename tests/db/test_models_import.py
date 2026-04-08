from app.db.base import Base
from app.db.models import FileObject, User


def test_models_are_registered_on_metadata() -> None:
    table_names = set(Base.metadata.tables.keys())

    assert "users" in table_names
    assert "files" in table_names
    assert User.__tablename__ == "users"
    assert FileObject.__tablename__ == "files"
