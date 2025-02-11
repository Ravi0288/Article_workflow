from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .journal import Journal_viewset

router = DefaultRouter()
router.register('journal', Journal_viewset, basename='journal')

urlpatterns = [
    path('', include(router.urls)),
]