import os
destination = '/ai/metadata/LOGDIR'
if not os.path.exists(destination):
    os.makedirs(destination)