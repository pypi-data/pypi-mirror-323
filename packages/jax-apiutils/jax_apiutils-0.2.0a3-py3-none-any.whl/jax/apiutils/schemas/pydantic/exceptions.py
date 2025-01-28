from .core import Error
from typing import Optional

__all__ = ["ErrorException"]


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
