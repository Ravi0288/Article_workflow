from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .unzip_ftp_archive import jsonify_ftp_zipped_xml_files


router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('download-from-ftp/', jsonify_ftp_zipped_xml_files),
]
