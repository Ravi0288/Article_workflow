from django.urls import path
from . import views

urlpatterns = [
    path('provider-access-view/', views.Provider_access_view, name='provider-access-report'),
    path('delivery-view/', views.delivery_view, name='delivery-report'),
]
