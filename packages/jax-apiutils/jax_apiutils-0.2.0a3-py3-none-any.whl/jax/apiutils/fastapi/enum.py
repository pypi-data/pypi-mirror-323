from enum import Enum

__all__ = ["ContentType"]


class ContentType(str, Enum):
    application_octet_stream = "application/octet-stream"
    application_zip = "application/zip"
    text_csv = "text/csv"
    text_plain = "text/plain"
