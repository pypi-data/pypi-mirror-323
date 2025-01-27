import logging

from fastapi import Request
from opentelemetry import trace


async def log_requests(request: Request, call_next):
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("log_requests"):
        logging.info(f"Request: {request.method} {request.url}")
        response = await call_next(request)
        logging.info(f"Response status: {response.status_code}")
    return response