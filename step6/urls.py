from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .migrate_to_step_6 import migrate_to_step6

urlpatterns = [
    path('migrate-to-step-6/', migrate_to_step6, name="migrate-to-step-6"),
]