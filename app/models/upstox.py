"""
Upstox authentication data models for MongoDB
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class UpstoxTokenModel(BaseModel):
    """Model for storing Upstox access tokens in MongoDB"""

    id: str = Field(
        default="upstox_token", alias="_id"
    )  # Single document with fixed ID
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "upstox_token",
                "access_token": "eyJ0eXAiOiJKV1QiLCJr...",
                "token_type": "Bearer",
                "expires_in": 86400,
                "expires_at": "2025-11-20T17:55:27.192142",
                "created_at": "2025-11-19T17:55:27.192142",
                "updated_at": "2025-11-19T17:55:27.192142",
            }
        }
