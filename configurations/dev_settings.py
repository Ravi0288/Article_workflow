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
# SECRET_KEY = get_env_variable('SECRET_KEY')

FERNET_KEY = b'KD2D79IHyj-01T9vC75gNxwDvhTvO370uqjPbzWIaAs='
# FERNET_KEY = get_env_variable('FERNET_KEY')


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# List of whitelisted host to be proivded here
ALLOWED_HOSTS = ['*']

# #########################################################################
# Application definition
INSTALLED_APPS = [
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'step1',
    'step2',
    'step3',
    'step4',
    'step5',
    'step6',
    'step7',
    'step8',
    'step9',
    'step10',
    'step11',
    'model',
    'mail_service',
    'accounts',
    'rest_framework.authtoken',
    # run django on https in development environment
    'sslserver',
    'reports',

    # MFA ENTRA
    # 'oauth2_provider'
]
# #########################################################################

# #########################################################################
# Middlewares to be used in this project
MIDDLEWARE = [
    # required middlewares for corseheader 
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Middleware to protect unauthorized access of any URL that is not authorized to logged in user
    # 'accounts.middleware.MenuAuthorizationMiddleware',
]
# #########################################################################

# #########################################################################
# CSRF Related settings
CSRF_TRUSTED_ORIGINS = ['https://article-workflow-admin-dev.nal.usda.gov']
CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOWED_ORIGINS = [
    'https://article-workflow-admin-dev.nal.usda.gov',
    'http://article-workflow-admin-dev.nal.usda.gov'
]
CORS_ORIGIN_WHITELIST = [
    'https://article-workflow-admin-dev.nal.usda.gov',
    'http://article-workflow-admin-dev.nal.usda.gov'
]

CORS_ALLOW_HEADERS = [
    "accept",
    "authorization",
    "content-type",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

CORS_ALLOW_METHODS = (
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
)
# #########################################################################


# Root URL file path
ROOT_URLCONF = 'configurations.urls'



###########################################################################
# Template for serving the result
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
# #########################################################################



# Project interface
WSGI_APPLICATION = 'configurations.wsgi.application'

# Database settings
DATABASES = {
    'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME':  BASE_DIR / 'article.sqlite3',
        },

        # 'pid_db': {
        #     'ENGINE': 'django.db.backends.sqlite3',
        #     'NAME':  BASE_DIR / 'pid.sqlite3',
        # }
}

# add router file for database settings
# DATABASE_ROUTERS = ['configurations.db_router.DB_route']

# specify the app_name for django to decide what database to access for what table
DATABASE_APPS_MAPPING = {'wf_data': 'default',
                        'handle_data':'handle_db',
                        'pid_data' : 'pid_db'}

# ##########################################################################





# ##########################################################################
# Default Django password validations
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
# ##########################################################################


# ##########################################################################
# Authentication
# This settings is for preventing the endpoints from unauthorised access.

OAUTH2_PROVIDER = {
    'ACCESS_TOKEN_EXPIRE_SECONDS': 36000,
    'AUTHORIZATION_CODE_EXPIRE_SECONDS': 300,
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}
# ##########################################################################



# #####################################
# Internationalization
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# ####################################

# # settings for proxy error
# if DEBUG==False:
#     SCRIPT_NAME = '/api'
#     FORCE_SCRIPT_NAME = SCRIPT_NAME

##################### Static file / Media file paths ####################
# s (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR,'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

CERT_ROOT = os.path.join(BASE_DIR, 'certificates')

MEDIA_URL = '/ai/metadata/'

# data downloaded in step one will be stored here
MEDIA_ROOT = '/ai/metadata'
ARCHIVE_ROOT = '/ai/metadata/ARCHIVE'
SUBMISSION_ROOT = '/ai/metadata/ARCHIVE/SUBMISSION' 
CROSSREF_ROOT = '/ai/metadata/ARCHIVE/CROSSREF' 
CHORUS_ROOT = '/ai/metadata/ARCHIVE/CHORUS'
TEMP_ROOT = '/ai/metadata/TEMP_DOWNLOAD'

# data once processed from step two will be stored here
ARTICLE_ROOT = '/ai/metadata/ARTICLES'
ARTICLE_CITATION = '/ai/metadata/ARTICLE_CITATION'
INVALID_XML_DIR = '/data/metada/INVALID_FILES'
MARC_XML_ROOT = '/ai/metadata/ARTICLE_MARC_XML'
ALMA_STAGING = '/ai/metadata/ALMA_STAGING'
ALMA_STAGING_BACKUP = '/ai/metadata/ALMA_STAGING_BACKUP'
##################### ############################ ####################


##################### ############################ ####################
# s3 upload maximum allowed number for each class of content
MERGE_USDA_MAX_LIMIT = 10000
NEW_USDA_MAX_LIMIT = 10000
MERGE_PUBLISHER_MAX_LIMIT = 10000
NEW_PUBLISHER_MAX_LIMIT = 10000


MERGE_USDA_MIN_LIMIT = 100
NEW_USDA_MIN_LIMIT = 100
MERGE_PUBLISHER_MIN_LIMIT = 100
NEW_PUBLISHER_MIN_LIMIT = 100

BASE_S3_URI = 's3://na-test-st01.ext.exlibrisgroup.com/01NAL_INST/upload/'
S3_BUCKET = 'na-test-st01.ext.exlibrisgroup.com'
S3_PREFIX = '01NAL_INST/upload/'
S3_URIS = {
    'new_usda_record':'18851814470007426/',
    'merge_usda_with_digital_files':'18851815290007426/',
    'merge_usda_without_digital_files':'21675299990007426/',
    'new_submission_records':'21176431170007426/',
    'new_submission_with_digital_files':'21176440550007426/',
    'new_submission_without_digital_files':'21451763880007426/',
}
#######################################################################

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


##################### Logger to log errors in file ####################
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'style': '{',
        },
        'semi-verbose': {
            'format': '{asctime} {levelname} {message}',
            'datefmt': '%Y-%m-%d %H:%M:%S',
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
            'filename': "/ai/metadata/LOGDIR/NAL_LIBRARY_SYSTEM.log",
            'maxBytes': 100000,
            'backupCount': 2,
            'formatter': 'verbose',
        },
        'journal_handler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': "/ai/metadata/LOGDIR/journal_record_warnings.log",
            'maxBytes': 100000,
            'backupCount': 3,
            'formatter': 'semi-verbose',
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
        'journal_logger': {
            'handlers': ['journal_handler'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
#########################################################################



##################### Email service related variables ####################
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mailproxy1.usda.gov'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_PASSWORD = get_env_variable('EPWD')
EMAIL_TO = ['ravi.parekh@usda.gov','chuck.schoppet@usda.gov']
##################### ############################### ####################

