from django.urls import path, include
from .migrate_to_step8 import migrate_to_step8


urlpatterns = [
    # path('', include(router.urls)),
    path('migrate-to-step-8/', migrate_to_step8, name="migrate-to-step-8")
]