from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .unzip_ftp_archive import jsonify_ftp_zipped_xml_files
from .make_single_object import segragate_records_with_multiple_articles
from step2.article import Article_attributes_viewset
from .article import migrate_to_step2, update_title, check_title, update_doi, find_key_main, check_doi, test_xml, \
    Unreadable_xml_files_viewset


router = DefaultRouter()
router.register('articles', Article_attributes_viewset, basename='articles')
router.register('unreadable-xml-files', Unreadable_xml_files_viewset, basename='unreadable_xml_files')

urlpatterns = [
    path('', include(router.urls)),
    path('migrate-to-step2/', migrate_to_step2),

    # Some endpoints for testing purposes only.
    # path('unzip-and-jasonify/', jsonify_ftp_zipped_xml_files),
    # path('make-single-object/', segragate_records_with_multiple_articles),
    # path('update-title/', update_title),
    # path('check/', check_title),
    # path('update-doi/', update_doi),
    # path('find-key/', find_key_main),
    # path('check-doi/', check_doi),
    # path('test-xml/', test_xml),
]
