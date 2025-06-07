from django.urls import path, include
from .migrate_to_step_11 import migrate_to_step11



urlpatterns = [
    path('migrate-to-step-11/', migrate_to_step11, name="migrate-to-step-11")
]