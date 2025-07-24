"""
MFA Enforcement Middleware for Django
Enforces multi-factor authentication on protected routes and manages session refresh.
"""

import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse, resolve
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class MFAEnforcementMiddleware(MiddlewareMixin):
    """
    Middleware to enforce MFA authentication on protected routes.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
        
        # URLs that are exempt from MFA enforcement
        self.exempt_urls = [
            'accounts:login',
            'accounts:microsoft_login',
            'accounts:microsoft_callback',
            'accounts:logout',
            'accounts:mfa_status',
            'admin:login',
            'admin:logout',
        ]
        
        # URL patterns that are exempt (regex patterns)
        self.exempt_patterns = [
            r'^/accounts/login.*',
            r'^/accounts/microsoft.*',
            r'^/accounts/logout.*',
            r'^/admin/login.*',
            r'^/admin/logout.*',
            r'^/static/.*',
            r'^/media/.*',
            r'^/favicon\.ico$',
        ]
    
    def process_request(self, request):
        """
        Process each request to enforce MFA authentication.
        """
        try:
            # Skip enforcement for exempt URLs
            if self._is_exempt_url(request):
                return None
            
            # Skip enforcement for non-authenticated users
            if not request.user.is_authenticated:
                return None
            
            # Check MFA verification status
            mfa_verified = request.session.get('mfa_verified', False)
            mfa_verified_at = request.session.get('mfa_verified_at')
            
            if not mfa_verified or not mfa_verified_at:
                logger.warning(f"MFA not verified for authenticated user: {request.user.username}")
                return self._redirect_to_mfa_login(request)
            
            # Check if MFA session is still valid (24 hours)
            try:
                verified_time = datetime.fromisoformat(mfa_verified_at.replace('Z', '+00:00'))
                if timezone.now() - verified_time > timedelta(hours=24):
                    logger.info(f"MFA session expired for user: {request.user.username}")
                    return self._redirect_to_mfa_login(request, "Your secure session has expired. Please re-authenticate.")
            except (ValueError, TypeError) as e:
                logger.error(f"Error parsing MFA verification time: {e}")
                return self._redirect_to_mfa_login(request)
            
            # MFA is valid, allow request to proceed
            return None
            
        except Exception as e:
            logger.error(f"Error in MFA enforcement middleware: {e}")
            return None
    
    def _is_exempt_url(self, request):
        """
        Check if the current URL is exempt from MFA enforcement.
        """
        try:
            # Check exempt URL names
            current_url = resolve(request.path_info)
            url_name = f"{current_url.namespace}:{current_url.url_name}" if current_url.namespace else current_url.url_name
            
            if url_name in self.exempt_urls:
                return True
            
            # Check exempt URL patterns
            import re
            for pattern in self.exempt_patterns:
                if re.match(pattern, request.path_info):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking exempt URL: {e}")
            return False
    
    def _redirect_to_mfa_login(self, request, message=None):
        """
        Redirect user to MFA login page.
        """
        try:
            # Store the current page for redirect after authentication
            request.session['next_page'] = request.get_full_path()
            
            # Add informative message
            if message:
                messages.warning(request, message)
            else:
                messages.info(request, "Multi-factor authentication is required to access this page.")
            
            # Redirect to login page
            return HttpResponseRedirect(reverse('accounts:login'))
            
        except Exception as e:
            logger.error(f"Error redirecting to MFA login: {e}")
            return HttpResponseRedirect('/accounts/login/')

class MFASessionRefreshMiddleware(MiddlewareMixin):
    """
    Middleware to refresh MFA session on activity.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """
        Refresh MFA session timestamp on authenticated activity.
        """
        try:
            # Only refresh for authenticated users with MFA
            if (request.user.is_authenticated and 
                request.session.get('mfa_verified', False)):
                
                # Update session activity timestamp
                request.session['last_activity'] = timezone.now().isoformat()
                
                # Extend session expiry
                request.session.set_expiry(86400)  # 24 hours
                
        except Exception as e:
            logger.error(f"Error in MFA session refresh middleware: {e}")
        
        return None

class MFASecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers for MFA-protected pages.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_response(self, request, response):
        """
        Add security headers to MFA-protected responses.
        """
        try:
            # Only add headers for authenticated MFA users
            if (request.user.is_authenticated and 
                request.session.get('mfa_verified', False)):
                
                # Add security headers
                response['X-Frame-Options'] = 'DENY'
                response['X-Content-Type-Options'] = 'nosniff'
                response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
                response['X-MFA-Protected'] = 'true'
                
        except Exception as e:
            logger.error(f"Error adding MFA security headers: {e}")
        
        return response
