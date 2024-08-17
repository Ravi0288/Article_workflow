"""
Django settings for nal_library project
"""
from pathlib import Path
import os
from .conf import get_env_variable

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-a(f9x&9kn8iwn&thlk_3j_48eu5rn0x*4h@xi+@6^%p-)=7-7k'
FERNET_KEY = b'KD2D79IHyj-01T9vC75gNxwDvhTvO370uqjPbzWIaAs='
# FERNET_KEY = get_env_variable('FERNET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


# List of whitelisted host to be proivded here
ALLOWED_HOSTS = ['*']

# CSRF Related settings
CSRF_TRUSTED_ORIGINS = ['http://*', 'https://*']
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_COOKIE_SECURE = False   # True if working with HTTPS else False


# Application definition
# ..................######
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'step1',
    'step2',
    'model',
    'mail_service',
    'authentication',
    'accounts',

    # run django on https in development environment
    'sslserver',

    # MFA ENTRA
    # 'oauth2_provider'
]
# ..................#######

# Middlewares to be used in this project
# ..................#############
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
# ..................#############




# Root URL file path
ROOT_URLCONF = 'configurations.urls'




# Template for serving the result
# ..................###############
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR, os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
# ..................#####################



# Project interface
WSGI_APPLICATION = 'configurations.wsgi.application'


# Default DB details
DB_ENGINE = os.environ['ARTICLE_DB_ENGINE']
DB_NAME = os.environ['ARTICLE_DB_NAME']
DB_USER = os.environ['ARTICLE_DB_USER']
DB_PASSWORD = os.environ['ARTICLE_DB_PASSWORD']
DB_HOST = os.environ['ARTICLE_DB_HOST']
DB_PORT = os.environ['ARTICLE_DB_PORT']

# # Handle DB details
HANDLE_DB_ENGINE = os.environ['HANDLE_DB_ENGINE']
HANDLE_DB_NAME = os.environ['HANDLE_DB_NAME']
HANDLE_DB_USER = os.environ['HANDLE_DB_USER']
HANDLE_DB_PASSWORD = os.environ['HANDLE_DB_PASSWORD']
HANDLE_DB_HOST = os.environ['HANDLE_DB_HOST']
HANDLE_DB_PORT = os.environ['HANDLE_DB_PORT']

# # PID DB details
PID_DB_ENGINE = os.environ['PID_DB_ENGINE']
PID_DB_NAME = os.environ['PID_DB_NAME']
PID_DB_USER = os.environ['PID_DB_USER']
PID_DB_PASSWORD = os.environ['PID_DB_PASSWORD']
PID_DB_HOST = os.environ['HANDLE_DB_HOST']
PID_DB_PORT = os.environ['PID_DB_PORT']


# Database settings
# ..................##################### #####################
DATABASES = {
   'default': {
   'ENGINE': DB_ENGINE,
   'NAME': DB_NAME,
   'USER': DB_USER,
   'PASSWORD': DB_PASSWORD,
   'HOST': DB_HOST,
   'PORT': DB_PORT,
    },

    # 'handles_db': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME':  BASE_DIR / 'handle.sqlite3',
    # },
    # 'pid_db': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME':  BASE_DIR / 'pid.sqlite3',
    # }
    'handle_db': {
        'ENGINE': HANDLE_DB_ENGINE,
        'NAME': HANDLE_DB_NAME,
        'USER': HANDLE_DB_USER,
        'PASSWORD': HANDLE_DB_PASSWORD,
        'HOST': HANDLE_DB_HOST,
        'PORT': HANDLE_DB_PORT,
    },

    'pid_db': {
        'ENGINE': PID_DB_ENGINE,
        'NAME': PID_DB_NAME,
        'USER': PID_DB_USER,
        'PASSWORD': PID_DB_PASSWORD,
        'HOST': PID_DB_HOST,
        'PORT': PID_DB_PORT,
    }
}


# add router file for database settings
DATABASE_ROUTERS = ['configurations.db_router.DB_route']

# specify the app_name for django to decide what database to access for what table
DATABASE_APPS_MAPPING = {'wf_data': 'default',
                        'handle_data':'handle_db',
                        'pid_data' : 'pid_db'}

# ..................##################### #####################




# Default Django password validations
# ..................#######################
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
# ..................##################


# configure outh settings
OAUTH2_PROVIDER = {
    'ACCESS_TOKEN_EXPIRE_SECONDS': 36000,
    'AUTHORIZATION_CODE_EXPIRE_SECONDS': 300,
}



# Rest framework authentication
# This settings is for preventing the endpoints from unauthorised access.
# ..................################
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication'
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}

# ..................##################




# Internationalization
# .........#####################
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# .........#####################



# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static',]

MEDIA_URL = '/media/'

# data downloaded in step one will be stored here
MEDIA_ROOT = BASE_DIR / 'ARCHIVE'
SUBMISSION_ROOT = MEDIA_ROOT / 'SUBMISSION' 
CROSSREF_ROOT = MEDIA_ROOT / 'CROSSREF' 
CHORUS_ROOT = MEDIA_ROOT / 'CHORUS' 

# data once processed from step one will stored at this location
ARTICLE_ROOT = BASE_DIR / 'ARTICLES'
INVALID_XML_DIR = BASE_DIR / 'INVALID_XML_FILES'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# HTTPS related settings
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SECURE_SSL_REDIRECT = True


# logger to log errors in file
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': "logs/NAL_LIBRARY_SYSTEM.log",
            'maxBytes': 100000,
            'backupCount': 2,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['logfile'],
            # DEBUG: Low-level system information
            # INFO: General system information
            # WARNING: Minor problems related information
            # ERROR: Major problems related information
            # CRITICAL: Critical problems related information
            # here we will log only error and critical (greater than error level)
            'level' : 'ERROR',
            'propagate': True,
        },
        'apps': {
            'handlers': ['logfile'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}


############### email service #####################

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mailproxy1.usda.gov'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_PASSWORD = get_env_variable('EPWD')


