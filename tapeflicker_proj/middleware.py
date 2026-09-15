from django.conf import settings

class ContentSecurityPolicyMiddleware:
    """
    Middleware that appends security headers to all outgoing responses.
    Mitigates XSS, frame injection, data leakage, and unauthorized browser features.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Safe Content Security Policy (CSP)
        # Allows self, Google assets (Identity/Auth/APIs/Fonts), YouTube embedded videos,
        # WebSocket local/remote connections, inline scripts with unsafe-inline (required for specific layouts).
        csp_rules = [
            "default-src 'self' http: https:",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' http: https: https://cdn.tailwindcss.com https://cdn.jsdelivr.net https://www.youtube.com https://www.gstatic.com https://apis.google.com https://www.google-analytics.com",
            "style-src 'self' 'unsafe-inline' http: https: https://fonts.googleapis.com https://cdnjs.cloudflare.com",
            "img-src 'self' data: http: https: https://*.googleusercontent.com https://images.unsplash.com https://www.gstatic.com https://res.cloudinary.com",
            "font-src 'self' data: http: https: https://fonts.gstatic.com",
            "frame-src 'self' http: https: https://www.youtube.com https://www.youtube-nocookie.com",
            "media-src 'self' data: blob: http: https: https://commondatastorage.googleapis.com https://assets.mixkit.co https://*.cloudinary.com",
            "connect-src 'self' http: https: ws: wss: https://identitytoolkit.googleapis.com https://securetoken.googleapis.com",
            "object-src 'none'",
            "base-uri 'self'"
        ]
        response["Content-Security-Policy"] = "; ".join(csp_rules)
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # In DEBUG / HTTP development mode, explicitly set HSTS max-age=0 to clear any cached HTTPS redirects in Chrome
        if getattr(settings, 'DEBUG', True) or not request.is_secure():
            response["Strict-Transport-Security"] = "max-age=0; includeSubDomains"
            
        return response

