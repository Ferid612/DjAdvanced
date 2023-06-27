from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

class RedirectMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.is_secure() and request.META.get('HTTP_X_FORWARDED_PROTO') != 'https':
            secure_url = request.build_absolute_uri(request.get_full_path()).replace('http://', 'https://')
            return redirect(secure_url)
        return self.get_response(request)