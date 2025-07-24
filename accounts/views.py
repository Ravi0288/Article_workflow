from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from .forms import UserForm, GroupForm
from django.contrib.auth import login, authenticate, logout
from .forms import CustomAuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from .authorization import Authorization
from .entra_login import entra_login, microsoft_callback, mfa_logout, check_mfa_status
import logging

logger = logging.getLogger(__name__)

@login_required
@csrf_exempt
def user_list(request):
    users = User.objects.all().order_by('username')
    
    # Pagination
    paginator = Paginator(users, 20)  # Show 10 items per page
    page_number = request.GET.get('page')  # Get the current page number
    page_obj = paginator.get_page(page_number)  # Get the page object for the current page

    context = {
        'title' : 'List of Users',
        'page_obj' : page_obj
    }

    return render(request, 'accounts/user_list.html', context=context)


@login_required
def user_create(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            form.save_m2m()
            return redirect('user-list')
    else:
        form = UserForm()
    return render(request, 'accounts/user_form.html', {'form': form})



@login_required
@csrf_exempt
def group_list(request):

    # groups = Group.objects.all().values_list()
    groups = Group.objects.all().order_by('name')

    # Pagination
    paginator = Paginator(groups, 20)  # Show 10 items per page
    page_number = request.GET.get('page')  # Get the current page number
    page_obj = paginator.get_page(page_number)  # Get the page object for the current page

    # prepare the date to be rendered on HTML page
    context = {
        'title' : 'List of Groups',
        'page_obj' : page_obj
    }

    return render(request, 'accounts/group_list.html', context=context)



@login_required
def group_create(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('group-list')
    else:
        form = GroupForm()
    return render(request, 'accounts/group_form.html', {'form': form})



'''
@csrf_exempt
def login_view(request):
    """
    Enhanced login view with MFA options and traditional authentication.
    """
    # Check if user is already authenticated with MFA
    if (request.user.is_authenticated and 
        request.session.get('mfa_verified', False)):
        return redirect('dashboard')
    
    # Handle traditional username/password authentication
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'traditional_login':
            form = CustomAuthenticationForm(request, data=request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                
                if user is not None:
                    login(request, user)
                    
                    # Set limited access session (not MFA verified)
                    request.session['mfa_verified'] = False
                    request.session['auth_method'] = 'traditional'
                    request.session['limited_access'] = True
                    
                    # Fetch authorized menu and store in session
                    try:
                        user_groups = user.groups.all()
                        menu_list = Authorization.objects.filter(
                            groups__in=user_groups
                        ).values_list('menu', flat=True)
                        request.session['menu_list'] = list(menu_list)
                    except Authorization.DoesNotExist:
                        request.session['menu_list'] = []
                    
                    messages.warning(
                        request, 
                        "You are logged in with limited access. For full system access, please use multi-factor authentication."
                    )
                    logger.info(f"Traditional login for user: {username}")
                    return redirect('dashboard')
                else:
                    messages.error(request, "Invalid username or password.")
            else:
                messages.error(request, "Please correct the errors below.")
        
        elif action == 'mfa_login':
            # Redirect to Microsoft MFA login
            return entra_login(request)
    
    else:
        form = CustomAuthenticationForm()
    
    context = {
        'form': form,
        'show_mfa_option': True,
        'mfa_required': getattr(settings, 'MFA_REQUIRED', False)
    }
    
    return render(request, 'accounts/login.html', context)
'''

@csrf_exempt
def login_view(request):

    if request.session.get('_auth_user_id'):
        return redirect('dashboard') 

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)

                # if logged in successfully, fetch authorized menu and store it to sesssion
                try:
                    user_groups = user.groups.all()
                    menu_list = Authorization.objects.filter(
                        groups__in=user_groups
                        ).values_list('menu', flat=True)
                    request.session['menu_list'] = list(menu_list)
                except Authorization.DoesNotExist:
                    request.session['menu_list'] = []

                return redirect('dashboard')  # Redirect to dashboard
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
@csrf_exempt
def dashboard_view(request):
    """
    Enhanced dashboard view with MFA status and authentication information.
    """
    # Get MFA status information
    mfa_verified = request.session.get('mfa_verified', False)
    auth_method = request.session.get('auth_method', 'unknown')
    mfa_verified_at = request.session.get('mfa_verified_at')
    limited_access = request.session.get('limited_access', False)
    
    # Calculate session validity
    session_valid = True
    session_expires_at = None
    
    if mfa_verified and mfa_verified_at:
        try:
            verified_time = datetime.fromisoformat(mfa_verified_at.replace('Z', '+00:00'))
            session_expires_at = verified_time + timedelta(hours=24)
            if timezone.now() > session_expires_at:
                session_valid = False
        except (ValueError, TypeError):
            session_valid = False
    
    # Determine user greeting and access level
    user_greeting = f"Welcome, {request.user.get_full_name() or request.user.username}!"
    
    if mfa_verified and session_valid:
        access_level = "Full Access (MFA Verified)"
        access_class = "success"
        security_message = "You have full system access with multi-factor authentication."
    elif limited_access:
        access_level = "Limited Access"
        access_class = "warning"
        security_message = "You have limited system access. Upgrade to MFA for full access."
    else:
        access_level = "Standard Access"
        access_class = "info"
        security_message = "Standard authentication active."
    
    context = {
        'heading': 'USDA Dashboard',
        'message': user_greeting,
        'user': request.user,
        'mfa_verified': mfa_verified,
        'auth_method': auth_method,
        'mfa_verified_at': mfa_verified_at,
        'session_valid': session_valid,
        'session_expires_at': session_expires_at,
        'limited_access': limited_access,
        'access_level': access_level,
        'access_class': access_class,
        'security_message': security_message,
        'show_mfa_upgrade': limited_access and not mfa_verified,
        'current_time': timezone.now()
    }
    
    return render(request, 'common/dashboard.html', context=context)

'''
def logout_view(request):
    """
    Enhanced logout view with MFA session cleanup.
    """
    return mfa_logout(request)
'''

def logout_view(request):
    logout(request)
    return redirect('login')

# MFA-specific view endpoints
def microsoft_login_view(request):
    """
    Microsoft MFA login endpoint.
    """
    return entra_login(request)

def microsoft_callback_view(request):
    """
    Microsoft OAuth2 callback endpoint.
    """
    return microsoft_callback(request)

def mfa_status_view(request):
    """
    MFA status API endpoint.
    """
    return check_mfa_status(request)

def upgrade_to_mfa(request):
    """
    Upgrade current session to MFA authentication.
    """
    if not request.user.is_authenticated:
        messages.error(request, "Please log in first.")
        return redirect('accounts:login')
    
    # Store the current page for redirect after MFA
    request.session['next_page'] = request.META.get('HTTP_REFERER', '/dashboard/')
    
    # Redirect to Microsoft MFA login
    return entra_login(request)

def mfa_required_view(request):
    """
    View displayed when MFA is required but not verified.
    """
    context = {
        'title': 'Multi-Factor Authentication Required',
        'message': 'This page requires multi-factor authentication.',
        'show_upgrade_option': request.user.is_authenticated
    }
    return render(request, 'accounts/mfa_required.html', context)
