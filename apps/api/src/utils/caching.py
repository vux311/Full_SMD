"""
Flask-Caching integration and cache utilities
"""
from flask_caching import Cache
from functools import wraps
from flask import request
import hashlib
import json

# Initialize cache (to be configured in create_app)
cache = Cache()


def cache_key_from_request():
    """
    Generate cache key from request parameters
    """
    args = request.args.to_dict()
    key_data = {
        'path': request.path,
        'args': args
    }
    key_string = json.dumps(key_data, sort_keys=True)
    return hashlib.md5(key_string.encode()).hexdigest()


def cached_response(timeout=300, key_prefix='view'):
    """
    Decorator to cache API responses
    
    Usage:
        @cached_response(timeout=600)
        def my_endpoint():
            pass
    
    Args:
        timeout: Cache timeout in seconds (default 5 minutes)
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{request.path}:{cache_key_from_request()}"
            
            # Try to get from cache
            cached = cache.get(cache_key)
            if cached is not None:
                return cached
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout=timeout)
            
            return result
        return wrapper
    return decorator


def invalidate_cache(key_pattern):
    """
    Invalidate cache entries matching pattern
    
    Args:
        key_pattern: Pattern to match cache keys (e.g., 'syllabus:*')
    """
    try:
        cache.delete_memoized(key_pattern)
    except Exception:
        # Fallback: clear all cache if pattern delete not supported
        cache.clear()


def cache_model(model_name, model_id, timeout=600):
    """
    Decorator to cache model by ID
    
    Usage:
        @cache_model('syllabus', syllabus_id)
        def get_syllabus(id):
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract ID from kwargs or args
            entity_id = kwargs.get('id') or (args[0] if args else None)
            
            if entity_id:
                cache_key = f"model:{model_name}:{entity_id}"
                cached = cache.get(cache_key)
                if cached is not None:
                    return cached
            
            result = func(*args, **kwargs)
            
            if entity_id and result:
                cache_key = f"model:{model_name}:{entity_id}"
                cache.set(cache_key, result, timeout=timeout)
            
            return result
        return wrapper
    return decorator
