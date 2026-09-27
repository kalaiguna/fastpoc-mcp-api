"""
API key authentication dependency.
Set API_KEY environment variable to enforce a specific key.
Defaults to 'dev-key-changeme' when not set.
"""
import os
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

_API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)
_EXPECTED_KEY = os.getenv("API_KEY", "dev-key-changeme")


def require_api_key(api_key: str = Security(_API_KEY_HEADER)) -> str:
    if not api_key or api_key != _EXPECTED_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return api_key
