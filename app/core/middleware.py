import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send
import uuid
from app.core.config import settings

logger = logging.getLogger(__name__)

class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """Middleware for logging request and response details."""
    
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Start timer
        start_time = time.time()
        
        # Client IP
        forwarded_for = request.headers.get("X-Forwarded-For")
        client_ip = forwarded_for.split(",")[0] if forwarded_for else request.client.host if request.client else None
        
        # Log request
        logger.info(
            f"Request started [ID: {request_id}]: {request.method} {request.url.path} from {client_ip}"
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            logger.info(
                f"Request completed [ID: {request_id}]: {request.method} {request.url.path} - "
                f"Status: {response.status_code}, Duration: {duration:.3f}s"
            )
            
            # Add custom headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(duration)
            
            return response
            
        except Exception as e:
            # Log exception
            duration = time.time() - start_time
            logger.error(
                f"Request failed [ID: {request_id}]: {request.method} {request.url.path} - "
                f"Error: {str(e)}, Duration: {duration:.3f}s"
            )
            raise

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.requests = {}
        self.rate_limit = settings.API_RATE_LIMIT
        self.window = settings.API_RATE_LIMIT_PERIOD
        
    async def dispatch(self, request: Request, call_next):
        # Extract client IP
        forwarded_for = request.headers.get("X-Forwarded-For")
        client_ip = forwarded_for.split(",")[0] if forwarded_for else request.client.host if request.client else "unknown"
        
        # Check API key for authenticated routes
        api_key = request.headers.get("Authorization", "").replace("Bearer ", "")
        
        # Use API key + IP as rate limit key for better tracking
        rate_limit_key = f"{api_key}:{client_ip}" if api_key else client_ip
        
        # Get current time
        current_time = time.time()
        
        # Clean up old entries
        self.requests = {k: v for k, v in self.requests.items() if current_time - v[-1] < self.window}
        
        # Check if key exists
        if rate_limit_key in self.requests:
            # Check number of requests in window
            if len(self.requests[rate_limit_key]) >= self.rate_limit:
                # If oldest request is within window, return 429
                if current_time - self.requests[rate_limit_key][0] < self.window:
                    logger.warning(f"Rate limit exceeded for {rate_limit_key}")
                    
                    # Return 429 Too Many Requests
                    headers = {
                        "Retry-After": str(int(self.window - (current_time - self.requests[rate_limit_key][0]))),
                        "X-RateLimit-Limit": str(self.rate_limit),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(self.requests[rate_limit_key][0] + self.window)),
                    }
                    
                    return Response(
                        content={"error": "Rate limit exceeded", "retry_after": headers["Retry-After"]},
                        status_code=429,
                        headers=headers,
                    )
                
                # Remove oldest request
                self.requests[rate_limit_key] = self.requests[rate_limit_key][1:]
        else:
            # Initialize new key
            self.requests[rate_limit_key] = []
        
        # Add current request time
        self.requests[rate_limit_key].append(current_time)
        
        # Add rate limit headers
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.rate_limit)
        response.headers["X-RateLimit-Remaining"] = str(self.rate_limit - len(self.requests[rate_limit_key]))
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.window))
        
        return response 