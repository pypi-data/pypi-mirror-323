"""Schemas for API Responses."""

import json
from datetime import datetime
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")

__all__ = ["ServerSentEvent"]


class ServerSentEventTemplate(BaseModel, Generic[T]):
    """Schema for server side events."""

    data: T
    id: Optional[str] = None
    retry: Optional[int] = None

    def model_dump_event(self) -> str:
        """Dump the model as an event."""
        # Get the current time and format it
        event_time = datetime.now().strftime("%H:%M:%S")

        # Add the 'time' key to the model's data
        event_data = self.data.dict()
        event_data["time"] = event_time

        # Prepare the event name as the Pydantic class name
        event_name = self.data.__class__.__name__

        # Construct the event string with optional id and retry
        event_parts = [f"event: {event_name}"]
        if self.id:
            event_parts.append(f"id: {self.id}")
        if self.retry:
            event_parts.append(f"retry: {self.retry}")

        event_parts.append(f"data: {json.dumps(event_data)}")

        return "\n".join(event_parts) + "\n\n"


class ServerSentEvent(str, Generic[T]):
    """Schema for server side events."""

    def __new__(cls, data: T, id: Optional[str] = None, retry: Optional[int] = None):
        return ServerSentEventTemplate[T](
            data=data, id=id, retry=retry
        ).model_dump_event()
