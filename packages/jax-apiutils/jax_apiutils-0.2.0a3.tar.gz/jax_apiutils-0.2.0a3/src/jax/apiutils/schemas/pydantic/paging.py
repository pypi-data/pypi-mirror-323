"""Schemas for API Responses."""

from collections.abc import Iterable
from typing import Optional, TypeVar
from urllib.parse import parse_qsl, urlencode

from pydantic import AnyUrl, BaseModel, Field
from starlette.datastructures import URL, MultiDict

T = TypeVar("T")

__all__ = ["PagingMixin", "PagingLinks", "Paging"]


class PagingMixin(BaseModel):
    limit: Optional[int] = Field(25, ge=0, le=1000)
    offset: Optional[int] = None


class PagingModelFormatter:
    @staticmethod
    def update_url(url, kwargs: dict) -> AnyUrl:
        params = MultiDict(parse_qsl(url.query, keep_blank_values=True))
        for key, value in kwargs.items():
            if isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
                params.setlist(str(key), list(value))
            else:
                params[str(key)] = str(value)
        query = urlencode(params.multi_items())
        return AnyUrl(str(url.replace(query=query)))

    @staticmethod
    def format_first(url, params: dict):
        try:
            del params["offset"]
        except KeyError:
            pass
        return PagingModelFormatter.update_url(url, params)

    @staticmethod
    def format_previous(url, offset, params: dict) -> Optional[AnyUrl]:
        try:
            offset = offset - params["limit"]
            if offset < 0:
                del params["offset"]
            return PagingModelFormatter.update_url(url, params)
        except KeyError:
            return None

    @staticmethod
    def format_next(
        url,
        offset,
        params: dict,
        total: Optional[int] = None,
    ) -> Optional[AnyUrl]:
        try:
            offset = offset + params["limit"]
            if total is None or offset < total:
                params["offset"] = offset
                return PagingModelFormatter.update_url(url, params)
        except KeyError:
            return None

    @staticmethod
    def format_last(
        url,
        params: dict,
        total: Optional[int] = None,
    ) -> Optional[AnyUrl]:
        if total:
            try:
                params["offset"] = total - params["limit"]
                return PagingModelFormatter.update_url(url, params)
            except KeyError:
                return None


class PagingLinks(BaseModel, PagingModelFormatter):
    """Schema for holding paging links."""

    first: Optional[AnyUrl] = None
    previous: Optional[AnyUrl] = None
    next: Optional[AnyUrl] = None
    last: Optional[AnyUrl] = None

    def __init__(self, url, total, **kwargs) -> None:
        these_kwargs = dict()
        needed_keys = ("first", "previous", "next", "last")
        for key in needed_keys:
            try:
                these_kwargs[key] = kwargs.pop(key)
            except KeyError:
                pass

        auto_kwargs = {
            "first": lambda u, o, k, t: self.format_first(u, k),
            "previous": lambda u, o, k, t: self.format_previous(u, o, k),
            "next": lambda u, o, k, t: self.format_next(u, o, k, t),
            "last": lambda u, o, k, t: self.format_last(u, k, t),
        }
        start_offset = kwargs.pop("offset", 0)

        for key in needed_keys:
            if key not in these_kwargs:
                these_kwargs[key] = auto_kwargs[key](url, start_offset, kwargs, total)

        super().__init__(**these_kwargs)


class Paging(BaseModel):
    """Schema for paging information."""

    page: Optional[int] = None
    items: Optional[int] = None
    total_pages: Optional[int] = None
    total_items: Optional[int] = None
    links: Optional[PagingLinks] = None

    def __init__(
        self, url: Optional[URL] = None, total: Optional[int] = None, **kwargs
    ) -> None:
        these_kwargs = dict()
        auto_kwargs = {
            "page": lambda k: k.get("offset") or 0 // k["limit"] + 1,
            "items": lambda k: k["limit"],
            "total_pages": lambda k: total // k["limit"] if total else None,
            "total_items": lambda k: total,
            "links": lambda k: PagingLinks(url, total, **k),
        }
        for key, value in auto_kwargs.items():
            try:
                these_kwargs[key] = kwargs.pop(key)
            except KeyError:
                try:
                    these_kwargs[key] = value(kwargs)
                except KeyError:
                    pass

        super().__init__(**these_kwargs)
