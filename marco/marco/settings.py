"""
Django settings for marco_portal project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

import os
import configparser
from os.path import abspath, dirname
from social.backends.google import GooglePlusAuth

# Absolute filesystem path to the Django project directory:
PROJECT_ROOT = dirname(dirname(dirname(abspath(__file__))))

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

ASSETS_DIR = os.path.realpath(os.path.join(BASE_DIR, '..', 'assets'))
COMPONENTS_DIR = os.path.realpath(os.path.join(BASE_DIR, '..', 'bower_components'))
STYLES_DIR = os.path.realpath(os.path.join(ASSETS_DIR, 'styles'))

CONFIG_FILE = os.path.normpath(os.path.join(BASE_DIR, 'config.ini'))


cfg = configparser.ConfigParser()
cfg.read(CONFIG_FILE)

if 'APP' not in cfg.sections():
    cfg['APP'] = {}

app_cfg = cfg['APP']

DEBUG = app_cfg.getboolean('DEBUG', True)
TEMPLATE_DEBUG = app_cfg.getboolean('TEMPLATE_DEBUG', True)

SECRET_KEY = app_cfg.get('SECRET_KEY', 'you forgot to set the secret key')
host_list = app_cfg.get('ALLOWED_HOSTS')
if type(host_list) == str:
    if '[' in host_list and ']' in host_list:
        import ast
        ALLOWED_HOSTS = ast.literal_eval(host_list)
    elif ',' in host_list:
        ALLOWED_HOSTS = host_list.split(',')
    else:
        ALLOWED_HOSTS = [host_list]
elif type(host_list) == list:
    ALLOWED_HOSTS = host_list
else:
    ALLOWED_HOSTS = [str(host_list)]

# Set logging to default, and then make admin error emails come through as HTML
from django.utils.log import DEFAULT_LOGGING
LOGGING = DEFAULT_LOGGING
LOGGING['handlers']['mail_admins']['include_html'] = True

# Application definition

INSTALLED_APPS = (
    'marco_site',
    # 'kombu.transport.django',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.gis',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    # 'django.contrib.webdesign',

    # 'p97settings',

    'email_log',
    'djcelery_email',
    'compressor',
    'taggit',
    'modelcluster',
    'rpc4django',
    'tinymce',

    'captcha',

    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail.core',

    'wagtail.contrib.sitemaps',

    'portal.base',
    'portal.menu',
    'portal.home',
    'portal.pages',
    'portal.ocean_stories',
    'portal.calendar',
    'portal.data_gaps',
    'portal.grid_pages',
    'portal.data_catalog',
    'portal.initial_data',
    'portal.welcome_snippet',
    'portal.news',
    'rest_framework',

    'flatblocks',

    'data_manager',
    'visualize',
    'features',
    'scenarios',
    'drawing',
    'manipulators',
    'explore',

    # Account management
    'social.apps.django_app.default',
    'accounts.apps.AccountsAppConfig',
    'django_social_share',
    'mapgroups',
    'import_export',

    # Multilayer Dimensions in Data Manager
    'nested_admin',
)

AUTHENTICATION_BACKENDS = (
    'social.backends.google.GoogleOAuth2',
    # 'social.backends.google.GoogleOpenId',
    'social.backends.facebook.FacebookOAuth2',
    'social.backends.twitter.TwitterOAuth',
    'django.contrib.auth.backends.ModelBackend',
)

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'wagtail.core.middleware.SiteMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
    'marco.host_site_middleware.HostSiteMiddleware',
]

# Valid site IDs are 1 and 2, corresponding to the primary site(1) and the
# test site(2)
SITE_ID = 1

INTERNAL_IPS = ('127.0.0.1',)

ROOT_URLCONF = 'marco.urls'
WSGI_APPLICATION = 'marco.wsgi.application'


if 'DATABASE' not in cfg.sections():
    cfg['DATABASE'] = {}

db_cfg = cfg['DATABASE']

default = {
    'ENGINE': db_cfg.get('ENGINE',
                      'django.contrib.gis.db.backends.postgis'),
}

if default['ENGINE'].endswith('spatialite'):
    SPATIALITE_LIBRARY_PATH = db_cfg.get('SPATIALITE_LIBRARY_PATH')
    default['NAME'] = db_cfg.get('NAME', os.path.join(BASE_DIR, 'marco.db'))
else:
    default['NAME'] = db_cfg.get('NAME')
    if cfg.has_option('DATABASE', 'USER'):
        default['USER'] = db_cfg.get('USER')
    if cfg.has_option('DATABASE', 'HOST'):
        default['HOST'] = db_cfg.get('HOST', 'localhost')
    default['PORT'] = db_cfg.getint('PORT', 5432)
    if cfg.has_option('DATABASE', 'PASSWORD'):
        default['PASSWORD'] = db_cfg.get('PASSWORD')

DATABASES = {'default': default}

if 'CACHES' not in cfg.sections():
    cfg['CACHES'] = {}

cache_cfg = cfg['DATABASE']

CACHES = {
    'default': {
        'BACKEND': cache_cfg.get('BACKEND'),
        'LOCATION': cache_cfg.get('LOCATION'),
        'KEY_PREFIX': 'marco_portal',
        'OPTIONS': {
            'CLIENT_CLASS': 'redis_cache.client.DefaultClient',
        }
    }
}

# TODO: Remove this when caching is installed
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = app_cfg.get('TIME_ZONE', 'UTC')
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_ROOT = app_cfg.get('STATIC_ROOT', os.path.join(BASE_DIR, 'static'))
STATIC_URL = app_cfg.get('STATIC_URL', '/static/')

STATICFILES_DIRS = (
    STYLES_DIR,
    COMPONENTS_DIR,
    ASSETS_DIR,
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'compressor.finders.CompressorFinder',
)

MEDIA_ROOT = app_cfg.get('MEDIA_ROOT', os.path.join(BASE_DIR, 'media'))
MEDIA_URL = app_cfg.get('MEDIA_URL', '/media/')


# Django compressor settings
COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'), # for wagtail
)

COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True



# Template configuration

from django.conf import global_settings

# Removed due to this: https://stackoverflow.com/a/39315587 - RDH 7/8/2019
# TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
#     'django.core.context_processors.request',
#     'social.apps.django_app.context_processors.backends',
#     'portal.base.context_processors.search_disabled',
# )


# TEMPLATE_LOADERS = global_settings.TEMPLATE_LOADERS + (
#     'apptemplates.Loader',
# )

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.realpath(os.path.join(os.path.dirname(__file__), 'templates').replace('\\', '/')),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages'
            ]
        },
    },
]

# Wagtail settings

LOGIN_URL = 'account:index'
# LOGIN_REDIRECT_URL = 'wagtailadmin_home'

WAGTAIL_SITE_NAME = 'MARCO Portal'

WAGTAILSEARCH_RESULTS_TEMPLATE = 'portal/search_results.html'


# WAGTAILSEARCH_BACKENDS = {
#     'default': {
#         'BACKEND': 'wagtail.search.backends.elasticsearch.ElasticSearch',
#         # 'URLS': ['https://iu20e5efzd:dibenj5fn5@point-97-elasticsear-6230081365.us-east-1.bonsai.io'],
#         'URLS': ['https://site:a379ac680e6aaa45f0c129c2cd28d064@bofur-us-east-1.searchly.com'],
#         'INDEX': 'marco_portal',
#         'TIMEOUT': 5,
#     }
# }

# Whether to use face/feature detection to improve image cropping - requires OpenCV
WAGTAILIMAGES_FEATURE_DETECTION_ENABLED = False

# Override the Image class used by wagtailimages with a custom one
WAGTAILIMAGES_IMAGE_MODEL = 'base.PortalImage'

FEEDBACK_IFRAME_URL = "//docs.google.com/a/pointnineseven.com/forms/d/1HMBSzAJ6QNpCOI01Z1CHHtrB0Fq6M081yXv5vBdBLm8/viewform?c=0&w=1"

# madrona-features
SHARING_TO_PUBLIC_GROUPS = ['Share with Public']
SHARING_TO_STAFF_GROUPS = ['Share with Staff']

# KML SETTINGS
KML_SIMPLIFY_TOLERANCE = 20 # meters
KML_SIMPLIFY_TOLERANCE_DEGREES = 0.0002 # Very roughly ~ 20 meters
KML_EXTRUDE_HEIGHT = 100
KML_ALTITUDEMODE_DEFAULT = 'absolute'

# madrona-scenarios
GEOMETRY_DB_SRID = 3857
GEOMETRY_CLIENT_SRID = 3857 #for latlon
GEOJSON_SRID = 3857

GEOJSON_DOWNLOAD = True  # force headers to treat like an attachment

# authentication
SOCIAL_AUTH_NEW_USER_URL = '/account/?new=true&login=django'
SOCIAL_AUTH_FACBEOOK_NEW_USER_URL = '/account/?new=true&login=facebook'
# SOCIAL_AUTH_GOOGLE_PLUS_NEW_USER_URL = '/account/?new=true&login=gplus'
SOCIAL_AUTH_TWITTER_NEW_USER_URL = '/account/?new=true&login=twitter'
SOCIAL_AUTH_GOOGLE_NEW_USER_URL = '/account/?new=true&login=google'

SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/account/?login=django'
# SOCIAL_AUTH_GOOGLE_PLUS_LOGIN_REDIRECT_URL = '/account/?login=gplus'
SOCIAL_AUTH_FACEBOOK_LOGIN_REDIRECT_URL = '/account/?login=facebook'
SOCIAL_AUTH_TWITTER_LOGIN_REDIRECT_URL = '/account/?login=twitter'
SOCIAL_AUTH_GOOGLE_LOGIN_REDIRECT_URL = '/account/?login=google'

# SOCIAL_AUTH_GOOGLE_PLUS_KEY = ''
# SOCIAL_AUTH_GOOGLE_PLUS_SECRET = ''
# SOCIAL_AUTH_GOOGLE_PLUS_SCOPES = (
#     'https://www.googleapis.com/auth/plus.login', # Minimum needed to login
#     'https://www.googleapis.com/auth/plus.profile.emails.read', # emails
# )

if 'SOCIAL_AUTH' not in cfg.sections():
    cfg['SOCIAL_AUTH'] = {}

social_cfg = cfg['SOCIAL_AUTH']

SOCIAL_AUTH_FACEBOOK_KEY = social_cfg.get('FACEBOOK_KEY', '')
SOCIAL_AUTH_FACEBOOK_SECRET = social_cfg.get('FACEBOOK_SECRET', '')
SOCIAL_AUTH_FACEBOOK_SCOPE = ['public_profile,email']

SOCIAL_AUTH_TWITTER_KEY = social_cfg.get('TWITTER_KEY', '')
SOCIAL_AUTH_TWITTER_SECRET = social_cfg.get('TWITTER_SECRET', '')

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = social_cfg.get('GOOGLE_KEY', '')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = social_cfg.get('GOOGLE_SECRET', '')
#SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = []
SOCIAL_AUTH_GOOGLE_OAUTH2_USE_DEPRECATED_API = True

# SOCIAL_AUTH_EMAIL_FORCE_EMAIL_VALIDATION = True
SOCIAL_AUTH_EMAIL_VALIDATION_FUNCTION = 'accounts.pipeline.send_validation_email'
SOCIAL_AUTH_EMAIL_VALIDATION_URL = '/account/validate'

SOCIAL_AUTH_DISCONNECT_REDIRECT_URL = '/'

# Our authentication pipeline
SOCIAL_AUTH_PIPELINE = (
    'accounts.pipeline.clean_session',

    # Get the information we can about the user and return it in a simple
    # format to create the user instance later. On some cases the details are
    # already part of the auth response from the provider, but sometimes this
    # could hit a provider API.
    'social.pipeline.social_auth.social_details',

    # Get the social uid from whichever service we're authing thru. The uid is
    # the unique identifier of the given user in the provider.
    'social.pipeline.social_auth.social_uid',

    # Verifies that the current auth process is valid within the current
    # project, this is were emails and domains whitelists are applied (if
    # defined).
    'social.pipeline.social_auth.auth_allowed',

    # Checks if the current social-account is already associated in the site.
    'social.pipeline.social_auth.social_user',

    # Make up a username for this person, appends a random string at the end if
    # there's any collision.
    'social.pipeline.user.get_username',

    # Confirm with the user that they really want to make an account, also
    # make them enter an email address if they somehow didn't
    'accounts.pipeline.confirm_account',

    # Send a validation email to the user to verify its email address.
    'social.pipeline.mail.mail_validation',

    # Create a user account if we haven't found one yet.
    'social.pipeline.user.create_user',

    # Create the record that associated the social account with this user.
    'social.pipeline.social_auth.associate_user',

    # Populate the extra_data field in the social record with the values
    # specified by settings (and the default ones like access_token, etc).
    'social.pipeline.social_auth.load_extra_data',

    # Update the user record with any changed info from the auth service.
    'social.pipeline.user.user_details',

    # Set up default django permission groups for new users.
    'accounts.pipeline.set_user_permissions',

    # Grab relevant information from the social provider (avatar)
    'accounts.pipeline.get_social_details',

    # 'social.pipeline.debug.debug',
    'accounts.pipeline.clean_session',
)

if 'EMAIL' not in cfg.sections():
    cfg['EMAIL'] = {}

email_cfg = cfg['EMAIL']

EMAIL_HOST = email_cfg.get('HOST', 'localhost')
EMAIL_PORT = email_cfg.getint('PORT', 8025)
if cfg.has_option('EMAIL', 'HOST_USER') and \
        cfg.has_option('EMAIL', 'HOST_PASSWORD'):
    EMAIL_HOST_USER = email_cfg.get('HOST_USER')
    EMAIL_HOST_PASSWORD = email_cfg.get('HOST_PASSWORD')

# EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'
CELERY_EMAIL_BACKEND = 'email_log.backends.EmailBackend'

DEFAULT_FROM_EMAIL = "MARCO Portal Team <portal@midatlanticocean.org>"
SERVER_EMAIL = "MARCO Site Errors <developers@pointnineseven.com>"
# for mail to admins/managers only
EMAIL_SUBJECT_PREFIX = app_cfg.get('EMAIL_SUBJECT_PREFIX', '[MARCO]') + ' '

if 'CELERY' not in cfg.sections():
    cfg['CELERY'] = {}

celery_cfg = cfg['CELERY']

CELERY_RESULT_BACKEND = celery_cfg.get('RESULT_BACKEND', '')
BROKER_URL = celery_cfg.get('BROKER_URL', '')

GA_ACCOUNT = app_cfg.get('GA_ACCOUNT', '')

ADMINS = (('KSDev', 'ksdev@ecotrust.org'),)

NOCAPTCHA = True
RECAPTCHA_PUBLIC_KEY = '6LevfQoUAAAAAPIKTQHJt3_Y2NDXkZQ3HYQHDNHk'
RECAPTCHA_PRIVATE_KEY = '6LevfQoUAAAAACp-4BPAgx4oMgeJrn1d9IMyReoI'

# OL2 doesn't support reprojecting rasters, so for WMS servers that don't provide
# EPSG:3857 we send it to a proxy to be re-projected.
WMS_PROXY = 'http://tiles.ecotrust.org/mapserver/'
WMS_PROXY_MAPFILE_FIELD = 'map'
WMS_PROXY_MAPFILE = '/mapfiles/generic.map'
WMS_PROXY_LAYERNAME = 'LAYERNAME'
WMS_PROXY_CONNECTION = 'CONN'
WMS_PROXY_FORMAT = 'FORMAT'
WMS_PROXY_VERSION = 'VERSION'
WMS_PROXY_SOURCE_SRS = 'SOURCESRS'
WMS_PROXY_SOURCE_STYLE = 'SRCSTYLE'
WMS_PROXY_TIME_EXTENT = 'TIMEEXT'
WMS_PROXY_TIME = 'TIME'
WMS_PROXY_TIME_DEFAULT = 'TIMEDEF'
WMS_PROXY_TIME_ITEM = 'TIMEITEM'
WMS_PROXY_GENERIC_LAYER = 'generic'
WMS_PROXY_TIME_LAYER = 'time'



if False:
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware',]
    INSTALLED_APPS += ['debug_toolbar',]
    DEBUG_TOOLBAR_PANELS2 = [
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.profiling.ProfilingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.templates.panel.TemplatesPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        # 'debug_toolbar.sql.panel.SQLPanel',
    ]
    import debug_toolbar.panels
