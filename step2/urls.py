from django.urls import path, include
from rest_framework.routers import DefaultRouter
from step2.article import Article_attributes_viewset
from .article import Unreadable_files_viewset, migrate_to_step2

router = DefaultRouter()
router.register('articles', Article_attributes_viewset, basename='articles')
router.register('unreadable-files', Unreadable_files_viewset, basename='unreadable-files')

urlpatterns = [
    path('', include(router.urls)),
    path('migrate-to-step2/', migrate_to_step2, name='migrate-to-step2'),
]
