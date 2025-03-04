from django.urls import path, include
from migrate_to_step_7 import migrate_to_step7

urlpatterns = [
    # path('', include(router.urls)),
    path('migrate-to-step-7/', migrate_to_step7, name="migrate-to-step-7"),
]