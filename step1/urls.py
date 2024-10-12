from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .archive import Archive_view
from .provider import Provider_viewset, Provider_meta_data_FTP_viewset, Provider_meta_data_API_viewset, \
    Fetch_history_viewset, Provider_meta_data_deposit_viewset
from .download_from_ftp import download_from_ftp
from .download_from_sftp import download_from_sftp
from .submission_api import download_from_submission_api
from .crossref_api import download_from_crossref_api
from .chorus_api import download_from_chorus_api
from .action_deposites import file_transfer_from_deposites



router = DefaultRouter()
router.register('archive-article', Archive_view, basename='archive-article')
router.register('providers-ftp', Provider_meta_data_FTP_viewset, basename='provider-ftp')
router.register('providers-api', Provider_meta_data_API_viewset, basename='provider-api')
router.register('providers-deposit', Provider_meta_data_deposit_viewset, basename='provider-deposite')
router.register('providers', Provider_viewset, basename='provider')
router.register('fetch-history', Fetch_history_viewset, basename='fetch-history')

urlpatterns = [
    path('', include(router.urls)),
    path('download-from-ftp/', download_from_ftp, name='download-from-ftp'),
    path('download-from-sftp/', download_from_sftp, name='download-from-sftp'),
    path('download-from-submission-api/', download_from_submission_api, name='download-from-submission-api'),
    path('download-from-crossref-api/', download_from_crossref_api, name='download-from-crossref-api'),
    path('download-from-chorus-api/', download_from_chorus_api, name='download-from-chorus-api'),
    path('action-deposites/', file_transfer_from_deposites, name='action-deposites'),
]