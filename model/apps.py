from django.apps import AppConfig
import os


class ModelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'model'

    def ready(self):

        # Import moved here to avoid early import error
        from model.provider import Providers
        providers = Providers.objects.all()

        for provider in providers:
            dir_path = f'/ai/metadata/ARTICLE_MARC_XML/{provider.working_name}'
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)