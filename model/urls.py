from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .handles import HandleViewSet, mint_handles

router = DefaultRouter()
router.register('', HandleViewSet, basename='handles')

urlpatterns = [
    path('', include(router.urls)),
    path('mint-handle', mint_handles, name="mint_handles"),
]