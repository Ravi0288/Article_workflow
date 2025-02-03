from django.urls import path, include
from rest_framework.routers import DefaultRouter
from step4.views import migrate_to_step4

router = DefaultRouter()
# router.register('articles', Article_viewset, basename='articles')

urlpatterns = [
    path('', include(router.urls)),
    path('migrate-to-step-4/', migrate_to_step4, name="migrate-to-step-4"),
]
