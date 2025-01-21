import logging
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("uvicorn")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        logger.info(f"Solicitud: {request.method} {request.url}")
        response = await call_next(request)
        logger.info(f"Respuesta: {response.status_code}")
        return response

def setup_logging(app):
    app.add_middleware(LoggingMiddleware)
