"""
Microsoft Entra ID OAuth2 Integration with MFA Enforcement
Handles the complete OAuth2 flow with JWT validation and MFA claims verification.
"""

import json
import logging
import secrets
import urllib.parse
from datetime import datetime, timedelta

import jwt
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)

# Microsoft Entra ID endpoints
MICROSOFT_AUTH_URL = "https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize"
MICROSOFT_TOKEN_URL = "https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
MICROSOFT_JWKS_URL = "https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys"
MICROSOFT_USERINFO_URL = "https://graph.microsoft.com/v1.0/me"

def get_microsoft_jwks():
    """
    Fetch Microsoft's JSON Web Key Set for token validation.
    """
    try:
        tenant_id = getattr(settings, 'MICROSOFT_TENANT_ID', 'common')
        jwks_url = MICROSOFT_JWKS_URL.format(tenant_id=tenant_id)
        response = requests.get(jwks_url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch JWKS: {e}")
        return None

def validate_jwt_token(token):
    """
    Validate JWT token signature and claims, including MFA verification.
    """
    try:
        # Get JWKS for signature validation
        jwks = get_microsoft_jwks()
        if not jwks:
            logger.error("Could not fetch JWKS for token validation")
            return None, "Unable to validate token signature"
        
        # Decode token header to get key ID
        header = jwt.get_unverified_header(token)
        kid = header.get('kid')
        
        if not kid:
            return None, "Token missing key ID"
        
        # Find the matching key
        key = None
        for jwk in jwks.get('keys', []):
            if jwk.get('kid') == kid:
                key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))
                break
        
        if not key:
            return None, "No matching key found for token"
        
        # Validate token
        client_id = getattr(settings, 'MICROSOFT_CLIENT_ID')
        tenant_id = getattr(settings, 'MICROSOFT_TENANT_ID', 'common')
        
        payload = jwt.decode(
            token,
            key,
            algorithms=['RS256'],
            audience=client_id,
            issuer=f"https://login.microsoftonline.com/{tenant_id}/v2.0"
        )
        
        # Verify MFA claim
        amr = payload.get('amr', [])
        mfa_verified = 'mfa' in amr or 'pwd' in amr and 'sms' in amr or 'pwd' in amr and 'otp' in amr
        
        if not mfa_verified:
            logger.warning(f"MFA not verified for user {payload.get('email', 'unknown')}. AMR: {amr}")
            return None, "Multi-factor authentication required"
        
        return payload, None
        
    except jwt.ExpiredSignatureError:
        return None, "Token has expired"
    except jwt.InvalidAudienceError:
        return None, "Invalid token audience"
    except jwt.InvalidIssuerError:
        return None, "Invalid token issuer"
    except jwt.InvalidTokenError as e:
        return None, f"Invalid token: {str(e)}"
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        return None, "Token validation failed"

def entra_login(request):
    """
    Initiate Microsoft Entra ID OAuth2 authentication with MFA enforcement.
    """
    try:
        # Generate state parameter for CSRF protection
        state = secrets.token_urlsafe(32)
        request.session['oauth_state'] = state
        
        # Build authorization URL
        tenant_id = getattr(settings, 'MICROSOFT_TENANT_ID', 'common')
        client_id = getattr(settings, 'MICROSOFT_CLIENT_ID')
        redirect_uri = getattr(settings, 'MICROSOFT_REDIRECT_URL')
        
        auth_params = {
            'client_id': client_id,
            'response_type': 'code',
            'redirect_uri': redirect_uri,
            'scope': 'openid profile email User.Read',
            'state': state,
            'response_mode': 'query',
            # Request MFA
            'prompt': 'login',
            'amr_values': 'mfa'
        }
        
        auth_url = MICROSOFT_AUTH_URL.format(tenant_id=tenant_id)
        full_auth_url = f"{auth_url}?{urllib.parse.urlencode(auth_params)}"
        
        logger.info(f"Initiating Microsoft authentication for user from IP: {request.META.get('REMOTE_ADDR')}")
        return redirect(full_auth_url)
        
    except Exception as e:
        logger.error(f"Error initiating Microsoft authentication: {e}")
        messages.error(request, "Authentication service temporarily unavailable. Please try again.")
        return redirect('accounts:login')

@csrf_exempt
@require_http_methods(["GET"])
def microsoft_callback(request):
    """
    Handle Microsoft OAuth2 callback and establish authenticated session.
    """
    try:
        # Verify state parameter
        state = request.GET.get('state')
        session_state = request.session.get('oauth_state')
        
        if not state or state != session_state:
            logger.warning(f"OAuth state mismatch. Session: {session_state}, Received: {state}")
            messages.error(request, "Invalid authentication request. Please try again.")
            return redirect('accounts:login')
        
        # Handle authorization errors
        error = request.GET.get('error')
        if error:
            error_description = request.GET.get('error_description', 'Unknown error')
            logger.warning(f"OAuth authorization error: {error} - {error_description}")
            
            if error == 'access_denied':
                messages.error(request, "Authentication was cancelled. Please try again.")
            else:
                messages.error(request, "Authentication failed. Please contact support.")
            
            return redirect('accounts:login')
        
        # Get authorization code
        code = request.GET.get('code')
        if not code:
            logger.error("No authorization code received from Microsoft")
            messages.error(request, "Authentication failed. Please try again.")
            return redirect('accounts:login')
        
        # Exchange code for tokens
        tenant_id = getattr(settings, 'MICROSOFT_TENANT_ID', 'common')
        token_url = MICROSOFT_TOKEN_URL.format(tenant_id=tenant_id)
        
        token_data = {
            'client_id': getattr(settings, 'MICROSOFT_CLIENT_ID'),
            'client_secret': getattr(settings, 'MICROSOFT_CLIENT_SECRET'),
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': getattr(settings, 'MICROSOFT_REDIRECT_URL'),
        }
        
        token_response = requests.post(token_url, data=token_data, timeout=10)
        token_response.raise_for_status()
        tokens = token_response.json()
        
        # Validate ID token and check MFA
        id_token = tokens.get('id_token')
        if not id_token:
            logger.error("No ID token received from Microsoft")
            messages.error(request, "Authentication incomplete. Please try again.")
            return redirect('accounts:login')
        
        payload, error = validate_jwt_token(id_token)
        if error:
            logger.error(f"Token validation failed: {error}")
            if "Multi-factor authentication required" in error:
                messages.error(request, "Multi-factor authentication is required for access.")
            else:
                messages.error(request, "Authentication verification failed.")
            return redirect('accounts:login')
        
        # Create or update user
        email = payload.get('email') or payload.get('preferred_username')
        name = payload.get('name', '')
        
        if not email:
            logger.error("No email found in Microsoft token payload")
            messages.error(request, "Unable to retrieve user information.")
            return redirect('accounts:login')
        
        # Get or create Django user
        user, created = User.objects.get_or_create(
            username=email,
            defaults={
                'email': email,
                'first_name': name.split(' ')[0] if name else '',
                'last_name': ' '.join(name.split(' ')[1:]) if ' ' in name else '',
            }
        )
        
        if not created:
            # Update existing user info
            user.email = email
            if name:
                user.first_name = name.split(' ')[0]
                user.last_name = ' '.join(name.split(' ')[1:]) if ' ' in name else ''
            user.save()
        
        # Log user in with MFA session
        login(request, user)
        
        # Store MFA verification info in session
        request.session['mfa_verified'] = True
        request.session['mfa_verified_at'] = timezone.now().isoformat()
        request.session['auth_method'] = 'microsoft_mfa'
        request.session['user_email'] = email
        
        # Set session expiry (24 hours)
        request.session.set_expiry(86400)  # 24 hours
        
        logger.info(f"Successful MFA authentication for user: {email}")
        messages.success(request, f"Welcome, {name or email}! You are logged in with multi-factor authentication.")
        
        # Redirect to dashboard or intended page
        next_page = request.session.get('next_page', '/dashboard/')
        if 'next_page' in request.session:
            del request.session['next_page']
        
        return redirect(next_page)
        
    except requests.RequestException as e:
        logger.error(f"Network error during Microsoft authentication: {e}")
        messages.error(request, "Authentication service temporarily unavailable. Please try again.")
        return redirect('accounts:login')
    except Exception as e:
        logger.error(f"Unexpected error in Microsoft callback: {e}")
        messages.error(request, "An unexpected error occurred. Please try again.")
        return redirect('accounts:login')
    finally:
        # Clean up session state
        if 'oauth_state' in request.session:
            del request.session['oauth_state']

def mfa_logout(request):
    """
    Securely log out user and clear MFA session data.
    """
    try:
        user_email = request.session.get('user_email', 'unknown')
        logger.info(f"User logout: {user_email}")
        
        # Clear all MFA-related session data
        mfa_keys = ['mfa_verified', 'mfa_verified_at', 'auth_method', 'user_email']
        for key in mfa_keys:
            if key in request.session:
                del request.session[key]
        
        # Django logout
        from django.contrib.auth import logout
        logout(request)
        
        messages.success(request, "You have been successfully logged out.")
        return redirect('accounts:login')
        
    except Exception as e:
        logger.error(f"Error during logout: {e}")
        return redirect('accounts:login')

def check_mfa_status(request):
    """
    API endpoint to check current MFA authentication status.
    """
    if not request.user.is_authenticated:
        return JsonResponse({
            'authenticated': False,
            'mfa_verified': False
        })
    
    mfa_verified = request.session.get('mfa_verified', False)
    mfa_verified_at = request.session.get('mfa_verified_at')
    auth_method = request.session.get('auth_method', 'unknown')
    
    # Check if MFA session is still valid (24 hours)
    session_valid = True
    if mfa_verified_at:
        try:
            verified_time = datetime.fromisoformat(mfa_verified_at.replace('Z', '+00:00'))
            if timezone.now() - verified_time > timedelta(hours=24):
                session_valid = False
        except:
            session_valid = False
    
    return JsonResponse({
        'authenticated': True,
        'mfa_verified': mfa_verified and session_valid,
        'auth_method': auth_method,
        'mfa_verified_at': mfa_verified_at,
        'session_valid': session_valid
    })
