"""Authentication Related Schemas."""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class User(BaseModel):
    """User model."""

    email: Optional[str] = None
    name: Optional[str] = None
    id: Optional[int] = None
    sso_id: str = Field(None, alias="sub")


class UserInternal(User):
    """Internal User model."""

    auth_header: dict = {}
    token: str
    permissions: Optional[List[str]] = None

    model_config = ConfigDict(populate_by_name=True)
