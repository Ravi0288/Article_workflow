from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .handles import HandleViewSet

router = DefaultRouter()
router.register('', HandleViewSet, basename='handles')

urlpatterns = [
    path('', include(router.urls)),
]