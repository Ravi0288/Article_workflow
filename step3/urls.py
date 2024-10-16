from django.urls import path, include
from rest_framework.routers import DefaultRouter
from step3.migrate_to_step_3 import jsonify_xml_file

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('migrate-to-step-3/', jsonify_xml_file, name="migrate-to-step-3"),
]
