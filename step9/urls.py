from django.urls import path, include
from .migrate_to_step_9 import migrate_to_step9



urlpatterns = [
    path('migrate-to-step-9/', migrate_to_step9, name="migrate-to-step-9"),
]