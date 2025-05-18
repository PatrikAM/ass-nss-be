"""
Application configuration settings.

This module contains all the configuration settings for the application,
including database connection strings and other environment-specific settings.
"""
import os
from typing import Optional

# Database connection URL
# Defaults to a local PostgreSQL instance if DATABASE_URL environment variable is not set
# Format: postgresql+asyncpg://username:password@host:port/database
DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@db:5432/testdb")

# Optional: Add more configuration settings here as needed
# Example:
# API_KEY: Optional[str] = os.getenv("API_KEY")
# DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
