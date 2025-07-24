from django.urls import path, include
from .migrate_to_step12 import migrate_to_step12

urlpatterns = [
    # path('', include(router.urls)),
    path('migrate-to-step-12/', migrate_to_step12, name="migrate-to-step-12")
]