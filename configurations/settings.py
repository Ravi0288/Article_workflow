"""
Django settings for nal_library project
"""
from pathlib import Path
import os
from .conf import get_env_variable

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ['SECRET_KEY']
FERNET_KEY = (os.environ['FERNET_KEY']).encode()

# Base URL for the application
# This should be set to the URL where the application is hosted.
BASE_URL = os.environ.get('BASE_URL', 'http://localhost:8000')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# This variable should be used only when using sqlite3
USING_SQLIT3 = False

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
    'step12',
    'model',
    'mail_service',
    'accounts',
    # 'rest_framework.authtoken',
    # run django on https in development environment
    'sslserver',
    'reports',
    'scheduler',
    'apscheduler'

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

    # MFA Enforcement Middleware
    # 'accounts.mfa_middleware.MFAEnforcementMiddleware',

    # Middleware to protect unauthorized access of any URL that is not authorized to logged in user
    # 'accounts.middleware.MenuAuthorizationMiddleware',
]
# #########################################################################

# #########################################################################
# CSRF Related settings
CSRF_TRUSTED_ORIGINS = [
    'https://article-workflow-admin.nal.usda.gov',
    'https://article-workflow-admin-dev.nal.usda.gov'
]

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOWED_ORIGINS = [
    'https://article-workflow-admin.nal.usda.gov',
    'http://article-workflow-admin.nal.usda.gov',
    'https://article-workflow-admin-dev.nal.usda.gov',
    'http://article-workflow-admin-dev.nal.usda.gov'
]
CORS_ORIGIN_WHITELIST = [
    'https://article-workflow-admin.nal.usda.gov',
    'http://article-workflow-admin.nal.usda.gov',
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

##########################################################################
# Default DB details
DB_ENGINE = os.environ['ARTICLE_DB_ENGINE']
DB_NAME = os.environ['ARTICLE_DB_NAME']
DB_USER = os.environ['ARTICLE_DB_USER']
DB_PASSWORD = os.environ['ARTICLE_DB_PASSWORD']
DB_HOST = os.environ['ARTICLE_DB_HOST']
DB_PORT = os.environ['ARTICLE_DB_PORT']

# # PID DB details
PID_DB_ENGINE = os.environ['PID_DB_ENGINE']
PID_DB_NAME = os.environ['PID_DB_NAME']
PID_DB_USER = os.environ['PID_DB_USER']
PID_DB_PASSWORD = os.environ['PID_DB_PASSWORD']
PID_DB_HOST = os.environ['PID_DB_HOST']
PID_DB_PORT = os.environ['PID_DB_PORT']
##########################################################################


# ##########################################################################
# Database settings
DATABASES = {
    'default': {
        'ENGINE': DB_ENGINE,
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
    },

    # # Handle DB is accesed directly. And the code is written in handles.py file in core python
    # 'pid_db': {
    #     'ENGINE': PID_DB_ENGINE,
    #     'NAME': PID_DB_NAME,
    #     'USER': PID_DB_USER,
    #     'PASSWORD': PID_DB_PASSWORD,
    #     'HOST': PID_DB_HOST,
    #     'PORT': PID_DB_PORT,
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
# (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR,'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
MEDIA_URL = os.environ['MEDIA_URL']

MEDIA_ROOT = os.environ['MEDIA_ROOT']

# Path not to be changed
TEMP_ROOT = os.path.join(MEDIA_ROOT,'TEMP_DOWNLOAD')
CERT_ROOT = os.path.join(BASE_DIR, 'certificates')

# Path can be changed
ARCHIVE_ROOT = os.path.join(MEDIA_ROOT, os.environ['ARCHIVE_DIR'])
ARTICLE_ROOT = os.path.join(MEDIA_ROOT, os.environ['ARTICLES_DIR'])
ARTICLE_CITATION = os.path.join(MEDIA_ROOT, os.environ['ARTICLE_CITATION_DIR'])
INVALID_XML_DIR = os.path.join(MEDIA_URL, os.environ['INVALID_FILES_DIR'])
MARC_XML_ROOT = os.path.join(MEDIA_ROOT,os.environ['ARTICLE_MARC_XML_DIR'])
ALMA_STAGING = os.path.join(MEDIA_ROOT, os.environ['ALMA_STAGING_DIR'])
ALMA_STAGING_BACKUP = os.path.join(MEDIA_ROOT, os.environ['ALMA_STAGING_BACKUP_DIR'])
ALMA_DIR_LIST = ['MERGE_USDA', 'NEW_USDA', 'MERGE_PUBLISHER', 'NEW_PUBLISHER']
JOURNAL_FILE_PATH = os.environ['JOURNAL_FILE_PATH']
##################### ############################ ####################


##################### ############################ ####################
# S3 upload maximum allowed number for each class of content
MERGE_USDA_MAX_LIMIT = int(os.environ.get('MERGE_USDA_MAX_LIMIT', 200))
NEW_USDA_MAX_LIMIT = int(os.environ.get('NEW_USDA_MAX_LIMIT', 200))
MERGE_PUBLISHER_MAX_LIMIT = int(os.environ.get('MERGE_PUBLISHER_MAX_LIMIT', 200))
NEW_PUBLISHER_MAX_LIMIT = int(os.environ.get('NEW_PUBLISHER_MAX_LIMIT', 200))

MERGE_USDA_MIN_LIMIT = int(os.environ.get('MERGE_USDA_MIN_LIMIT', 10000))
NEW_USDA_MIN_LIMIT = int(os.environ.get('NEW_USDA_MIN_LIMIT', 10000))
MERGE_PUBLISHER_MIN_LIMIT = int(os.environ.get('MERGE_PUBLISHER_MIN_LIMIT', 10000))
NEW_PUBLISHER_MIN_LIMIT = int(os.environ.get('NEW_PUBLISHER_MIN_LIMIT', 10000))

BASE_S3_URI = os.environ['BASE_S3_URI'] #'s3://na-test-st01.ext.exlibrisgroup.com/01NAL_INST/upload/'
S3_BUCKET = os.environ['S3_BUCKET']  #'na-test-st01.ext.exlibrisgroup.com'
S3_SUFIX = os.environ['S3_SUFIX']  #'01NAL_INST/upload/'
S3_URIS = {
    'new_usda_record':os.environ['new_usda_record'],
    'merge_usda_with_digital_files':os.environ['merge_usda_with_digital_files'],
    'merge_usda_without_digital_files':os.environ['merge_usda_without_digital_files'],
    'new_publisher_records':os.environ['new_publisher_records'],
    'new_publisher_with_digital_files':os.environ['new_publisher_with_digital_files'],
    'new_publisher_without_digital_files':os.environ['new_publisher_without_digital_files'],
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
        'standard': {
            'format': '[{asctime}] {levelname} {name} - {message}',
            'style': '{',
        },
    },
    'handlers': {
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.environ['COMMON_LOGFILE_NAME'],
            'maxBytes': 100000,
            'backupCount': 2,
            'formatter': 'verbose',
        },
        'journal_handler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.environ['JOURNAL_LOGFILE_NAME'],
            'maxBytes': 100000,
            'backupCount': 3,
            'formatter': 'semi-verbose',
        },
        'cron_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.environ['CRONE_LOGFILE_NAME'],
            'formatter': 'standard',
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
        'scheduler': {
            'handlers': ['cron_file'],
            'level': 'INFO',
            'propagate': False,
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

'''
##################### Microsoft Entra ID MFA Configuration ####################
# Microsoft Entra ID OAuth2 Configuration
# These should be set as environment variables in production
MICROSOFT_CLIENT_ID = os.environ.get('MICROSOFT_CLIENT_ID', '')
MICROSOFT_CLIENT_SECRET = os.environ.get('MICROSOFT_CLIENT_SECRET', '')
MICROSOFT_TENANT_ID = os.environ.get('MICROSOFT_TENANT_ID', 'common')
MICROSOFT_REDIRECT_URL = os.environ.get('MICROSOFT_REDIRECT_URL', 'http://localhost:8000/accounts/microsoft/callback/')

# MFA Session Configuration
MFA_SESSION_TIMEOUT = 24 * 60 * 60  # 24 hours in seconds
MFA_SESSION_REFRESH_THRESHOLD = 60 * 60  # 1 hour in seconds

# MFA Middleware Configuration
MFA_EXEMPT_URLS = [
    'accounts/login/',
    'accounts/microsoft/',
    'accounts/microsoft/callback/',
    'accounts/logout/',
    'admin/',
    'static/',
    'media/',
]

# Security Settings for Production
if not DEBUG:
    # Force HTTPS in production
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # Secure cookies
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # Additional security headers
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
##################### ##################################### ####################
'''
