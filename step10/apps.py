from django.apps import AppConfig
import os
from django.conf import settings


class Stp10Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'step10'

    def ready(self):
        dir_list = ['MERGE_USDA', 'NEW_USDA', 'MERGE_PUBLISHER', 'NEW_PUBLISHER']
        for dir in dir_list:
            dir_path = os.path.join(settings.ALMA_STAGING, dir)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
