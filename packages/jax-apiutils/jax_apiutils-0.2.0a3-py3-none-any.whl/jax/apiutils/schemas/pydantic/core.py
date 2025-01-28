"""Schemas for API Responses."""

from typing import Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel

from .paging import URL, Paging

T = TypeVar("T")

__all__ = ["Error", "BaseResponse", "Response", "CollectionResponse", "GenericResponse"]


class Ping(BaseModel):
    """Schema for ping response."""

    message: str = "connected"


class Error(BaseModel):
    """Schema for error responses."""

    code: Optional[str] = None
    num_code: Optional[int] = None
    message: str


class BaseResponse(BaseModel):
    """Schema for base response."""

    errors: Optional[List[Error]] = None
    info: Optional[Dict] = None


class Response(BaseResponse, Generic[T]):
    """Schema for response."""

    object: Optional[T] = None

    def __init__(self, *args, **kwargs):
        if args:
            kwargs["object"] = args[0]
        super().__init__(**kwargs)


class CollectionResponse(BaseResponse, Generic[T]):
    """Schema for API responses with collections."""

    data: Optional[List[T]]
    paging: Optional[Paging] = None

    def __init__(
        self, *args, url: Optional[URL] = None, total: Optional[int] = None, **kwargs
    ) -> None:
        these_kwargs = dict()
        auto_kwargs = {
            "data": lambda a, k: a[0],
            "errors": lambda a, k: a[1],
            "paging": lambda a, k: Paging(url, total, **k) if url else None,
            "info": lambda a, k: a[2],
        }
        for key, value in auto_kwargs.items():
            try:
                these_kwargs[key] = kwargs.pop(key)
            except KeyError:
                try:
                    these_kwargs[key] = value(args, kwargs)
                except (KeyError, IndexError):
                    continue
        super().__init__(**these_kwargs)


class GenericResponse(Response, CollectionResponse, Generic[T]):
    """Schema for generic response."""

    object: Optional[T] = None
    data: Optional[List[T]] = None

    def __init(self, *args, **kwargs):
        if args:
            kwargs["object"] = args[0]
            kwargs["data"] = args[1]
        super().__init__(**kwargs)
