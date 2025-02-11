from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .journal import Journal_viewset
from .migrate_to_step_4 import migrate_to_step4

router = DefaultRouter()
router.register('journal', Journal_viewset, basename='journal')

urlpatterns = [
    path('', include(router.urls)),
    path('migrate-to-step-4/', migrate_to_step4, name="migrate-to-step-4"),
]