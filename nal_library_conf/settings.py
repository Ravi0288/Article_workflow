"""
Django settings for nal_library project
"""
import ftplib
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-a(f9x&9kn8iwn&thlk_3j_48eu5rn0x*4h@xi+@6^%p-)=7-7k'

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
    'actions'
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
ROOT_URLCONF = 'nal_library_conf.urls'




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
WSGI_APPLICATION = 'nal_library_conf.wsgi.application'




# Database settings
# ..................#####################
DATABASES = {
    'default': {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': 'usda',
    'USER':'root',
    'PASSWORD':'admin',
    'HOST':'localhost',
    'PORT':'3306',
    }
}

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
MEDIA_ROOT = BASE_DIR / 'article_library'
UPLOAD_ROOT = BASE_DIR / 'uploads'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# FTP Settings variables
# .........#################
HOSTNAME = "192.168.152.132"
USERNAME = "admin"
PASSWORD = "admin"
# .........#################




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
            'filename': "NAL_LIBRARY_SYSTEM.log",
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