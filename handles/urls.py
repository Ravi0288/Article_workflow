from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .handles import HandleViewSet, mint_handles, mint_handle_main_function

router = DefaultRouter()
router.register('', HandleViewSet, basename='handles')

urlpatterns = [
    path('', include(router.urls)),
    path('mint-handle', mint_handles, name="mint-handles-api"),
    path('mint', mint_handle_main_function, name="mint-handles"),
]