from django.apps import AppConfig
import os
from django.conf import settings


class ModelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'model'

    def ready(self):

        # Import moved here to avoid early import error
        from model.provider import Providers
        providers = Providers.objects.all()

        for provider in providers:
            dir_path = os.path.join(settings.MARC_XML_ROOT, provider.working_name)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
               
        dir_list = settings.ALMA_DIR_LIST
        for dir in dir_list:
            dir_path = os.path.join(settings.ALMA_STAGING, dir)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)