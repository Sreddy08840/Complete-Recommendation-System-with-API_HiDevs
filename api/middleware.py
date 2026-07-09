
import logging
import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to generate unique request IDs, log requests/responses,
    and add request ID to response headers.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Record start time
        start_time = time.time()
        
        # Process the request
        response: Response = await call_next(request)
        
        # Calculate response time
        process_time = (time.time() - start_time) * 1000  # in milliseconds
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        # Prepare log message with structured data
        log_data = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "response_time_ms": round(process_time, 2)
        }
        
        # Log the request details - manually attach attributes to record using a filter or just format manually
        # Let's format the log message directly for simplicity and reliability
        logger.info(
            f"Request processed | request_id={request_id} | method={request.method} | url={str(request.url)} | "
            f"status_code={response.status_code} | response_time_ms={round(process_time, 2)}"
        )
        
        return response

