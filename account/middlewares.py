
from django.shortcuts import render


class NotAllowedMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        print("Before View")
        response = render(request, 'account/not_allowed.html')
        print("After View")
        return response
