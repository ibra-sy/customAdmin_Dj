"""
Middleware pour la redirection selon l'interface admin choisie
"""
from django.shortcuts import redirect
from django.urls import reverse

from .auth_views import SESSION_INTERFACE_KEY, INTERFACE_MODERN


class AdminInterfaceRedirectMiddleware:
    """
    Redirige les utilisateurs connectés vers l'interface choisie (moderne ou classique).
    - Si interface=modern et accès à /admin/ (index) → redirige vers /admin/modern/
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path.rstrip('/')
        if (request.user.is_authenticated and 
            request.user.is_staff and
            path == '/admin' and
            request.session.get(SESSION_INTERFACE_KEY) == INTERFACE_MODERN):
            return redirect(reverse('admin:modern_dashboard'))
        return self.get_response(request)
