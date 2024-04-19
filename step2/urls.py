from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .unzip_ftp_archive import jsonify_ftp_zipped_xml_files
from .make_single_object import make_single_object_from_multiple


router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('unzip-and-jasonify/', jsonify_ftp_zipped_xml_files),
    path('make-single-object/', make_single_object_from_multiple),
]
