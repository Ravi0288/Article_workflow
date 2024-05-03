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

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


# List of whitelisted host to be proivded here
ALLOWED_HOSTS = ['*']


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
    'step2'
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




# Database settings
# ..................#####################
DATABASES = {
   'default': {
   'ENGINE': 'django.db.backends.mysql',
   'NAME': 'article_workflow_db',
   'USER':get_env_variable('DBUSER'),
   'PASSWORD':get_env_variable('DBPSWD'),
   'HOST':'localhost',
   'PORT':'3306',
   }
}

# DATABASE_DIR = os.path.join(BASE_DIR, 'db.sqlite3')
# DATABASES = {
#      'default': {
#          'ENGINE': 'django.db.backends.sqlite3',
#          'NAME': DATABASE_DIR,
#      }
# }

# ..................#####################




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





# Rest framework authentication
# This settings is for preventing the endpoints from unauthorised access.
# ..................################
# REST_FRAMEWORK = {
#     'DEFAULT_AUTHENTICATION_CLASSES': [
#         'rest_framework.authentication.TokenAuthentication',
#     ],
#     'DEFAULT_PERMISSION_CLASSES':(
#         'rest_framework.permissions.IsAuthenticated',
#     ),
# }
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
MEDIA_ROOT = BASE_DIR / 'ARCHIVE_ARTICLE'
SUBMISSION_ROOT = MEDIA_ROOT / 'SUBMISSION' 
CROSSREF_ROOT = MEDIA_ROOT / 'CROSSREF' 
CHORUS_ROOT = MEDIA_ROOT / 'CHORUS' 

# data once processed from step one will stored at this location
ARTICLE_ROOT = BASE_DIR / 'ARTICLES'
INVALID_XML_DIR = BASE_DIR / 'INVALID_XML_FILES'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



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

