from django.urls import path
from django.urls import path, include
from .fallback import  callback  
from .entra_login import entra_login
# from rest_framework.routers import DefaultRouter
# from .authorization import Authorization_viewset, get_url_names
from .authorization import create_authorization
from . import views

# router = DefaultRouter()
# router.register('authorized-menu', Authorization_viewset, basename='authorized-menu')

urlpatterns = [
    # path('', include(router.urls)),
    path('users/', views.user_list, name='user-list'),
    path('users/create/', views.user_create, name='user-create'),
    path('groups/', views.group_list, name='group-list'),
    path('groups/create/', views.group_create, name='group-create'),
    path('login/', views.login_view, name='login'),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # for entra
    path('entra-login/', entra_login, name='entra-login'),
    path('callback/', callback, name='callback'),
    # path('get_url_names/', get_url_names, name='get_url_names'),
    path('create-authorization/', create_authorization, name='create-authorization')
]
