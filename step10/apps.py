from django.apps import AppConfig
import os


class Stp10Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'step10'

    def ready(self):
        dir_list = ['MERGE_USDA', 'NEW_USDA', 'MERGE_PUBLISHER', 'NEW_PUBLISHER']
        for item in dir_list:
            dir_path = f'/ai/metadata/ALMA_STAGING/{item}'
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
