from django.urls import path, include
from rest_framework.routers import DefaultRouter
from step2.article import Article_attributes_viewset
# from .article import migrate_to_step2, Unreadable_xml_files_viewset
# from .process_files import migrate_to_step2, Unreadable_xml_files_viewset
from .article import migrate_to_step2, Unreadable_xml_files_viewset


router = DefaultRouter()
router.register('articles', Article_attributes_viewset, basename='articles')
router.register('unreadable-xml-files', Unreadable_xml_files_viewset, basename='unreadable_xml_files')

urlpatterns = [
    path('', include(router.urls)),
    path('migrate-to-step2/', migrate_to_step2, name='migrate-to-step2')
]
