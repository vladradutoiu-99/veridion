import uuid
import time

from typing import Dict
from app.utils import get_logger

from starlette.requests import Request
from starlette.datastructures import MutableHeaders

from starlette.types import ASGIApp, Message, Scope, Receive, Send

from opentelemetry import trace

from app.api.logger import logger


class LoggingMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request = Request(scope)

        span = trace.get_current_span()

        request_id = str(uuid.uuid4())
        trace_id = format(span.get_span_context().trace_id, "x")
        path = request.url.path

        async def send_with_logging(message: Message):
            if message["type"] == "http.response.start":
                status = message["status"]

                nonlocal request_id
                nonlocal trace_id
                nonlocal start_time
                nonlocal path

                elapsed = time.time() - start_time

                loc_headers: Dict[str, str] = {}
                loc_headers["x-request-id"] = request_id
                loc_headers["x-trace-id"] = trace_id

                headers = MutableHeaders(scope=message)
                for key, value in loc_headers.items():
                    headers.append(key, value)

                logger.trace(
                    "Request ended on path '{path}' with status_code '{status_code}'. Time: '{elapsed}'",
                    path=path,
                    status_code=status,
                    elapsed=elapsed,
                    type="trace"
                )

            await send(message)

        with logger.contextualize(
            requestId=request_id, traceId=trace_id
        ):
            logger.bind(
                path=request.url.path,
                method=request.method,
                type="trace"
            ).trace("Request started on path '{path}'", path=request.url.path)

            start_time = time.time()

            return await self.app(scope, receive, send_with_logging)
