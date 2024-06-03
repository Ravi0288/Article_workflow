from django.urls import path, include
from rest_framework.routers import DefaultRouter



router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    # path('migrate-to-step2/', migrate_to_step2),
]
