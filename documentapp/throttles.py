from rest_framework.throttling import UserRateThrottle

class PdfGenerationThrottle(UserRateThrottle):
    """Throttle for PDF generation to prevent abuse. Limit to 5 requests per minute."""
    # Match the scope name used in REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']
    scope = 'pdf_gen'

    def get_cache_key(self, request, view):  # Override to use user ID for throttling instead of IP address
        if not request.user.is_authenticated:
            return None  # Only throttle authenticated users
        return self.cache_format % {
            'scope': self.scope,
            'ident': request.user.pk  # Use user ID as identifier
        }