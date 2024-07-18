from django.urls import path, include
from rest_framework.routers import DefaultRouter
from step3.process_files import jsonify_xml_file



router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('jsonify-xml-files/', jsonify_xml_file),
]
