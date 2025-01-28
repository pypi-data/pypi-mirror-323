"""Custom FastAPI Responses."""

import logging
from typing import AsyncIterable, Optional, Callable, Generic

from fastapi.requests import Request
from fastapi.responses import StreamingResponse

from jax.apiutils.schemas.pydantic.core import Ping
from jax.apiutils.schemas.pydantic.server_sent_event import ServerSentEvent, T


logger = logging.getLogger("uvicorn.error")


class ServerSentEventResponse(StreamingResponse, Generic[T]):
    """
    Enhanced Server-Sent Event response with connection monitoring.

    Maintains the original event generation logic while adding
    request disconnection handling.
    """

    def __init__(
        self,
        iterator: AsyncIterable,
        request: Request,
        on_disconnect: Optional[Callable] = None,
        send_pings: bool = False,
    ):
        """
        Initialize the SSE response.

        :param iterator: Async iterator yielding events
        :param request: Starlette request object for disconnect checking
        :param on_disconnect: Optional callback when connection is lost
        :param send_pings: Whether to send ping events when iterable yields None
        """
        self._request = request
        self._on_disconnect = on_disconnect

        async def event_generator():
            try:
                async for item in iterator:
                    # Check for client disconnection before yielding
                    if await self._request.is_disconnected():
                        # Call optional disconnect handler
                        logger.info("Noticed disconnected request in SSE response.")
                        if self._on_disconnect:
                            logger.info(
                                "Client disconnected, running disconnect handler."
                            )
                            await self._on_disconnect()
                        break

                    if item is not None:
                        yield ServerSentEvent[T](data=item)
                    elif send_pings:
                        yield ServerSentEvent[T](data=Ping())

            except Exception as e:
                logger.error(f"Error in SSE stream: {e}")
                raise e

        super().__init__(
            content=event_generator(),
            media_type="text/event-stream",
        )
