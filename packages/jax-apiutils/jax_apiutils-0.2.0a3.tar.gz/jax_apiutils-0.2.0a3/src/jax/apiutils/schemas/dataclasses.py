"""Dataclass Implementations of the schemas.

Only use when necessary, it's preferred to use the Pydantic based schemas
since they have more features and are more flexible.
"""

from dataclasses import dataclass, field
from typing import Dict, Generic, List, Optional, TypeVar

__all__ = [
    "Error",
    "ErrorException",
    "PagingLinks",
    "Paging",
    "Response",
    "CollectionResponse",
    "GenericResponse",
]


T = TypeVar("T")


@dataclass
class Ping:
    """Ping schema."""

    message: str = "connected"


@dataclass
class Error:
    """Error schema."""

    message: str
    code: Optional[str] = None
    num_code: Optional[int] = None


@dataclass
class BaseResponse:
    """Base response schema."""

    errors: Optional[List[Error]] = None
    info: Optional[Dict] = None


@dataclass
class PagingLinks:
    """Schema for holding paging links."""

    first: Optional[str] = None
    previous: Optional[str] = None
    next: Optional[str] = None
    last: Optional[str] = None


@dataclass
class Paging:
    """Schema for paging information."""

    page: Optional[int] = None
    items: Optional[int] = None
    total_pages: Optional[int] = None
    total_items: Optional[int] = None
    links: Optional[PagingLinks] = None


@dataclass
class Response(BaseResponse, Generic[T]):
    """Response schema."""

    object: Optional[T] = None

    def __init__(
        self,
        object: Optional[T] = None,
        errors: Optional[List[Error]] = None,
        info: Optional[Dict] = None,
    ):
        super().__init__(errors=errors, info=info)
        self.object = object


@dataclass
class CollectionResponse(BaseResponse, Generic[T]):
    """Collection response schema."""

    data: Optional[List[T]] = None
    paging: Optional[Paging] = None

    def __init__(
        self,
        data: Optional[T] = None,
        paging: Optional[Paging] = None,
        errors: Optional[List[Error]] = None,
        info: Optional[Dict] = None,
    ):
        super().__init__(errors=errors, info=info)
        self.data = data
        self.paging = paging


@dataclass
class GenericResponse(Response, CollectionResponse, Generic[T]):
    """Generic response schema."""

    object: Optional[T] = None
    data: Optional[List[T]] = None

    def __init__(
        self,
        data: Optional[T] = None,
        paging: Optional[Paging] = None,
        errors: Optional[List[Error]] = None,
        info: Optional[Dict] = None,
    ):
        super().__init__(errors=errors, info=info)
        self.object = object
        self.data = data
        self.paging = paging


class ErrorException(Exception):
    def __init__(
        self, message: str, code: Optional[str] = None, num_code: Optional[int] = None
    ) -> None:
        self.code = code
        self.message = message
        self.num_code = num_code

    def to_error(self) -> Error:
        return Error(
            code=self.code,
            num_code=self.num_code,
            message=self.message,
        )
