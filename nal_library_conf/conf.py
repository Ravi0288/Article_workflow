import os
from django.core.exceptions import ImproperlyConfigured


# this function need environment name variable to access the stored values like password / secret keys
# This is rquired to avoid storing the password in plain text.
def get_env_variable(var_name):
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = KeyError % var_name
        raise ImproperlyConfigured(error_msg)
 