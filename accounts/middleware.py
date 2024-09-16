from django.shortcuts import redirect, render
from django.urls import resolve
from django.conf import settings

class MenuAuthorizationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.process_request(request)
        if response:
            return response
        response = self.get_response(request)
        return response

    def process_request(self, request):

        if request.user.is_staff:
            return None

        # Get the current path
        current_url_name = resolve(request.path_info).url_name

        # List of URLs that don't need menu authorization checks (e.g., login, logout, dashboard)
        exempt_urls = ['login', 'logout', 'dashboard']

        # Check if the URL requires menu authorization
        if current_url_name not in exempt_urls:
            # Get the menu list from the session
            menu_list = request.session.get('menu_list', [])

            # Check if the current URL is in the menu list
            if current_url_name not in menu_list:
                # If not, redirect to the dashboard
                # return redirect('dashboard')
                context = {
                    'heading' : 'USDA Dashboard',
                    'message' : 'You are trying to access the URL that you are not authorized. This will be reported'
                }

                return render(request, 'common/dashboard.html', context=context)

        return None
