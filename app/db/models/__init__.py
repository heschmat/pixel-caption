"""
This module imports all the database models used in the application, 
making them available for use in other parts of the codebase.
This matters for Alembic autogeneration.

⚠️ If you add a new model, 
make sure to import it here so that Alembic can detect it when generating migrations.
"""
from app.db.models.file import FileObject
from app.db.models.user import User

__all__ = ["User", "FileObject"]
