import os
from django.conf import settings

destination= []
destination.append(os.environ['JOURNAL_LOGFILE_NAME'])
destination.append(os.environ['COMMON_LOGFILE_NAME'])
for dir in destination:
    if not os.path.exists(dir):
        os.makedirs(dir)




