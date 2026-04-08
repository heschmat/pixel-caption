"""
This module sets up the database connection and session management for the application using SQLAlchemy.
It creates an engine based on the database URL specified in the configuration, 
and defines a session factory that can be used to create database sessions throughout the application.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Create the SQLAlchemy engine using the database URL from the settings
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)

# Create a configured "Session" class
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)