from django.http import HttpResponseRedirect
from django.urls import reverse

class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Logic to check authentication status and URL path
        if not request.user.is_authenticated and (request.path == '/login/chef' or request.path == '/login/prof') :
            return HttpResponseRedirect(reverse('login'))  # Redirect to login page
        return self.get_response(request)
