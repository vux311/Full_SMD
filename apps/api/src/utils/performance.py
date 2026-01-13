"""
Performance monitoring decorator and utilities
"""
import time
import functools
from utils.logging_config import get_logger

logger = get_logger(__name__)


def monitor_performance(func):
    """
    Decorator to monitor function execution time and log performance metrics
    
    Usage:
        @monitor_performance
        def my_function():
            pass
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        func_name = f"{func.__module__}.{func.__name__}"
        
        try:
            logger.debug(f"Starting {func_name}")
            result = func(*args, **kwargs)
            
            duration_ms = (time.time() - start_time) * 1000
            logger.info(
                f"Completed {func_name}",
                extra={"duration_ms": duration_ms, "status": "success"}
            )
            
            # Warn if execution takes too long
            if duration_ms > 1000:  # > 1 second
                logger.warning(
                    f"Slow execution detected: {func_name} took {duration_ms:.2f}ms"
                )
            
            return result
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                f"Failed {func_name}: {str(e)}",
                extra={"duration_ms": duration_ms, "status": "error"},
                exc_info=True
            )
            raise
    
    return wrapper


def log_api_request(func):
    """
    Decorator to log API requests with details
    
    Usage:
        @log_api_request
        def my_endpoint():
            pass
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        from flask import request, g
        
        start_time = time.time()
        endpoint = f"{request.method} {request.path}"
        
        # Get user_id from Flask g context if available
        user_id = getattr(g, 'user_id', None)
        
        logger.info(
            f"API Request: {endpoint}",
            extra={
                "method": request.method,
                "path": request.path,
                "user_id": user_id,
                "ip": request.remote_addr
            }
        )
        
        try:
            result = func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000
            
            # Extract status code from response
            status_code = 200
            if isinstance(result, tuple) and len(result) > 1:
                status_code = result[1]
            
            logger.info(
                f"API Response: {endpoint}",
                extra={
                    "duration_ms": duration_ms,
                    "status_code": status_code,
                    "user_id": user_id
                }
            )
            
            return result
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                f"API Error: {endpoint} - {str(e)}",
                extra={
                    "duration_ms": duration_ms,
                    "status_code": 500,
                    "user_id": user_id
                },
                exc_info=True
            )
            raise
    
    return wrapper
