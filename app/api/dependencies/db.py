"""
This module defines a dependency for getting a database session in FastAPI.
The `get_db` function is a generator that yields a database session, 
and ensures that the session is properly closed after use.

This allows us to easily inject a database session 
into the FastAPI route handlers using the `Depends` mechanism.

Example usage in a FastAPI route handler:
```python
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from app.api.dependencies.db import get_db
router = APIRouter()
@router.get("/items/")
def read_items(db: Session = Depends(get_db)):
    # Use the db session to query the database
    items = db.query(Item).all()
    return items
```
"""
from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
