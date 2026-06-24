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
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://cdn.jsdelivr.net https://www.youtube.com https://www.gstatic.com https://apis.google.com https://www.google-analytics.com",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com",
            "img-src 'self' data: https://*.googleusercontent.com https://images.unsplash.com https://www.gstatic.com https://res.cloudinary.com",
            "font-src 'self' data: https://fonts.gstatic.com",
            "frame-src 'self' https://www.youtube.com https://www.youtube-nocookie.com",
            "connect-src 'self' ws: wss: https://identitytoolkit.googleapis.com https://securetoken.googleapis.com",
            "object-src 'none'",
            "base-uri 'self'"
        ]
        response["Content-Security-Policy"] = "; ".join(csp_rules)
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response
