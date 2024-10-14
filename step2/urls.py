from django.urls import path, include
from rest_framework.routers import DefaultRouter
from step2.article import Article_attributes_viewset
# from .article import migrate_to_step2, Unreadable_xml_files_viewset
# from .process_files import migrate_to_step2, Unreadable_xml_files_viewset
from .article import Unreadable_xml_files_viewset, migrate_to_step2
from .splitter import test_cases
# from .article_new import migrate_to_step2

router = DefaultRouter()
router.register('articles', Article_attributes_viewset, basename='articles')
router.register('unreadable-xml-files', Unreadable_xml_files_viewset, basename='unreadable-xml-files')

urlpatterns = [
    path('', include(router.urls)),
    path('migrate-to-step2/', migrate_to_step2, name='migrate-to-step2'),
    path('test_cases/', test_cases, name='test_case')
]
