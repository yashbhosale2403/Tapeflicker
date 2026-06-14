from django.core.cache import cache
from django.http import JsonResponse
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def ratelimit(key_prefix, limit=5, period=60):
    """
    Cache-based IP rate limiter decorator.
    Tracks client IP address and enforces request limit within the observation period (in seconds).
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Resolve remote IP address safely behind reverse proxies (like Render)
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0].strip()
            else:
                ip = request.META.get('REMOTE_ADDR')
            
            cache_key = f"ratelimit:{key_prefix}:{ip}"
            request_count = cache.get(cache_key, 0)
            
            if request_count >= limit:
                logger.warning(f"Rate limit exceeded for IP {ip} on view {view_func.__name__} (Prefix: {key_prefix})")
                return JsonResponse({
                    'status': 'error', 
                    'message': f'Too many attempts. Please wait {period} seconds and try again.'
                }, status=429)
            
            # Increment request counter. First request sets TTL window.
            if request_count == 0:
                cache.set(cache_key, 1, period)
            else:
                cache.set(cache_key, request_count + 1, period)
                
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
