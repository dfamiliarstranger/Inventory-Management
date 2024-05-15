# middleware.py

from django.shortcuts import redirect
from django.urls import reverse

class HandlePageNotFoundMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # Check if response status code is 404 (Page Not Found)
        if response.status_code == 404:
            if request.user.is_authenticated:
                # Redirect to error page if logged in
                return redirect(reverse('error_page'))
            else:
                # Redirect to home page if not logged in
                return redirect(reverse('home'))
        return response
