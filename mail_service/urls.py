from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import Email_history_viewset, Email_notification_viewset

router = DefaultRouter()
router.register('email-address', Email_notification_viewset, basename='email-addresses')
router.register('email-history', Email_history_viewset, basename='email-history')

urlpatterns = [
    path('', include(router.urls)),
]
