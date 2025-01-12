from django.urls import path, include
from rest_framework.routers import DefaultRouter
from step3.migrate_to_step_3 import migrate_to_step3

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('migrate-to-step-3/', migrate_to_step3, name="migrate-to-step-3"),
]
