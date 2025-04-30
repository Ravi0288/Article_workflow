from django.urls import path, include
from .migrate_to_step_10 import migrate_to_step10



urlpatterns = [
    path('migrate-to-step-10/', migrate_to_step10, name="migrate-to-step-10"),
]