from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .migrate_to_step_5 import migrate_to_step5


urlpatterns = [
    path('migrate-to-step-5/', migrate_to_step5, name="migrate-to-step-5")
]