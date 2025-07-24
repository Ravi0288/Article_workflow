from django.urls import path, include
from .authorization import create_authorization
from . import views

# URL namespace for accounts app
app_name = 'accounts'

urlpatterns = [
    # User and Group Management
    path('users/', views.user_list, name='user-list'),
    path('users/create/', views.user_create, name='user-create'),
    path('groups/', views.group_list, name='group-list'),
    path('groups/create/', views.group_create, name='group-create'),
    
    # Authentication Endpoints
    path('login/', views.login_view, name='login'),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # MFA Endpoints
    # path('microsoft/', views.microsoft_login_view, name='microsoft_login'),
    # path('microsoft/callback/', views.microsoft_callback_view, name='microsoft_callback'),
    # path('mfa/status/', views.mfa_status_view, name='mfa_status'),
    # path('mfa/upgrade/', views.upgrade_to_mfa, name='mfa_upgrade'),
    # path('mfa/required/', views.mfa_required_view, name='mfa_required'),
    
    # Authorization
    path('create-authorization/', create_authorization, name='create-authorization'),
]
