from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .unzip_ftp_archive import jsonify_ftp_zipped_xml_files
from .make_single_object import segragate_records_with_multiple_articles
from step2.article import Article_attributes_viewset
from .article import migrate_to_step2, update_title, check_title, update_doi


router = DefaultRouter()
router.register('articles', Article_attributes_viewset, basename='articles')

urlpatterns = [
    path('', include(router.urls)),
    # path('unzip-and-jasonify/', jsonify_ftp_zipped_xml_files),
    # path('make-single-object/', segragate_records_with_multiple_articles),
    path('migrate-to-step2/', migrate_to_step2),
    path('update-title/', update_title),
    path('check/', check_title),
    path('update-doi/', update_doi),

]
