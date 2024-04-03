from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .archive_article import Archived_article_attribute_view
from .providers import Provider_viewset, Provider_meta_data_FTP_viewset, Provider_meta_data_API_viewset, \
    Fetch_history_viewset
from .email_notification import Email_notification_viewset, Email_history_viewset
from .download_from_api import download_from_api
from .download_from_ftp import download_from_ftp
from .submission_api import download_from_submission_api


router = DefaultRouter()
router.register('archive-article', Archived_article_attribute_view, basename='archive-articl')
router.register('providers-ftp', Provider_meta_data_FTP_viewset, basename='provider-ftp')
router.register('providers-api', Provider_meta_data_API_viewset, basename='provider-api')
router.register('providers', Provider_viewset, basename='provider')
router.register('email-address', Email_notification_viewset, basename='email-addresses')
router.register('fetch-history', Fetch_history_viewset, basename='fetch-history')
router.register('email-history', Email_history_viewset, basename='email-history')

urlpatterns = [
    path('', include(router.urls)),
    path('download-from-api/', download_from_api),
    path('download-from-ftp/', download_from_ftp),
    path('download-from-submission-api/', download_from_submission_api)
]
