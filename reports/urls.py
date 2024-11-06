from django.urls import path
from . import views

urlpatterns = [
    path('provider-access-view/', views.Provider_access_view, name='provider-access-report'),
    path('backlog-view/', views.backlog_view, name='backlog-report'),
]
