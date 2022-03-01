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
# from social.backends.google import GooglePlusAuth

# Absolute filesystem path to the Django project directory:
PROJECT_ROOT = dirname(dirname(dirname(abspath(__file__))))

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

ASSETS_DIR = os.path.realpath(os.path.join(BASE_DIR, '..', 'assets'))
COMPONENTS_DIR = os.path.realpath(os.path.join(BASE_DIR, '..', 'bower_components'))
STYLES_DIR = os.path.realpath(os.path.join(ASSETS_DIR, 'styles'))

MP_PROJECT_CONFIG = os.environ.get("MP_PROJECT_CONFIG", default='config.ini')
CONFIG_FILE = os.path.normpath(os.path.join(BASE_DIR, MP_PROJECT_CONFIG))


cfg = configparser.ConfigParser()
cfg.read(CONFIG_FILE)

if 'APP' not in cfg.sections():
    cfg['APP'] = {}

app_cfg = cfg['APP']

DEBUG = app_cfg.getboolean('DEBUG', True)

APP_NAME = app_cfg.get('APP_NAME', 'Marine Planner')
APP_URL = app_cfg.get('APP_URL', '')
APP_TEAM_NAME = app_cfg.get('APP_TEAM_NAME', "{} Team".format(APP_NAME))

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


CATALOG_TECHNOLOGY = None


# Application definition
try:
    # Thanks to tgandor for this inspiration to handle two different wagtail
    #      versions conditionally while performing this terrible merge:
    #   https://djangosnippets.org/snippets/3048/
    __import__('wagtail.contrib.forms')
    # Wagtail v2
    WAGTAIL_VERSION = 2

    INSTALLED_APPS = [
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
        'wagtail.contrib.styleguide',
        'wagtail.contrib.sitemaps',
        'wagtail.locales',
    ]
except ImportError as e:
    # print(e)
    # Wagtail v1 for merging in old MidA Portal
    WAGTAIL_VERSION = 1
    INSTALLED_APPS = [
        'wagtail.core',
        'wagtail.admin',
        'wagtail.docs',
        'wagtail.snippets',
        'wagtail.users',
        'wagtail.sites',
        'wagtail.images',
        'wagtail.embeds',
        'wagtail.search',
        'wagtail.redirects',
        'wagtail.forms',
        'wagtail.contrib.wagtailsitemaps',
    ]

try:
    __import__('django_redis')
    REDIS_PACKAGE_NAME = 'django_redis'
    INSTALLED_APPS += ['django_redis',]
except ImportError as e:
    REDIS_PACKAGE_NAME = 'redis_cache'


INSTALLED_APPS += [
    'marco_site',
    # 'kombu.transport.django',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.gis',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',
    # 'django.contrib.webdesign',
    'django.contrib.humanize',

    # 'p97settings',

    'email_log',
    'djcelery_email',
    'compressor',
    'taggit',
    'modelcluster',
    'rpc4django',
    'tinymce',

    'captcha',
    'social_django',
    # 'django_redis',

    'portal.base',
    'portal.menu',
    'portal.home',
    'portal.pages',
    'portal.ocean_stories',
    'portal.calendar',
    'portal.data_gaps',
    'portal.grid_pages',
    'portal.data_catalog',
    'portal.gp2_catalog',
    'portal.initial_data',
    'portal.welcome_snippet',
    'portal.news',
    'rest_framework',

    'flatblocks',
    'wagtailimportexport',

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
]

AUTHENTICATION_BACKENDS = (
    # 'social.backends.google.GoogleOAuth2',
    # 'social.backends.google.GoogleOpenId',
    # 'social.backends.facebook.FacebookOAuth2',
    # 'social.backends.twitter.TwitterOAuth',
    'django.contrib.auth.backends.ModelBackend',
)

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # 'wagtail.core.middleware.SiteMiddleware',
    # 'wagtail.contrib.redirects.middleware.RedirectMiddleware',
    'marco.host_site_middleware.HostSiteMiddleware',
]

# FILE_UPLOAD_HANDLERS = [
#     'django.core.files.uploadhandler.MemoryFileUploadHandler',
#     'django.core.files.uploadhandler.TemporaryFileUploadHandler'
# ]

if WAGTAIL_VERSION > 1:
    try:
        __import__('wagtail.core.middleware.SiteMiddleware')
        MIDDLEWARE += [
            'wagtail.core.middleware.SiteMiddleware',
        ]
    except ImportError as e:
        # https://docs.wagtail.io/en/stable/releases/2.11.html#sitemiddleware-moved-to-wagtail-contrib-legacy
        MIDDLEWARE += [
            'wagtail.contrib.legacy.sitemiddleware.SiteMiddleware',
        ]
        WAGTAIL_VERSION = 2.11
    MIDDLEWARE += [
        'wagtail.contrib.redirects.middleware.RedirectMiddleware',
    ]
else:
    MIDDLEWARE += [
        'wagtail.core.middleware.SiteMiddleware',
        'wagtail.redirects.middleware.RedirectMiddleware',
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
    # default['NAME'] = os.environ.get("SQL_DATABASE", "ocean_portal"),
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

# ------------------------------------------------------------------------------
# Redis sessions and caching
# ------------------------------------------------------------------------------
# SESSION_ENGINE = 'redis_sessions.session'
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
SESSION_REDIS_HOST = 'localhost'
SESSION_REDIS_PORT = 6379
SESSION_REDIS_DB = 0

if REDIS_PACKAGE_NAME == 'redis_cache':
    {
        'default': {
            'BACKEND': 'redis_cache.RedisCache',
            'LOCATION': '/home/midatlantic/run/redis.sock',
            'KEY_PREFIX': 'marco_portal',
            'OPTIONS': {
                'CLIENT_CLASS': 'redis_cache.client.DefaultClient'
            },
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': cache_cfg.get('BACKEND', 'django_redis.cache.RedisCache'),
            'LOCATION': cache_cfg.get('LOCATION', 'redis://127.0.0.1:6379/1'),
            'KEY_PREFIX': 'marco_portal',
            'OPTIONS': {
                'CLIENT_CLASS': cache_cfg.get('CLIENT_CLASS', 'django_redis.client.DefaultClient'),
            }
        }
    }

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = app_cfg.get('TIME_ZONE', 'UTC')
USE_I18N = True
USE_L10N = True
USE_TZ = True
WAGTAIL_I18N_ENABLED = False
WAGTAIL_CONTENT_LANGUAGES = LANGUAGES = [
    ('en', "English"),
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_ROOT = app_cfg.get('STATIC_ROOT', os.path.join(BASE_DIR, 'static'))
STATIC_URL = app_cfg.get('STATIC_URL', '/static/')
STATIC_CORE = app_cfg.get('STATIC_CORE', '/usr/local/apps/marco_portal_static/')

STATICFILES_DIRS = (
    STYLES_DIR,
    COMPONENTS_DIR,
    ASSETS_DIR,
    STATIC_CORE,
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

COMPRESS_ENABLED = app_cfg.getboolean('COMPRESS_ENABLED', True)
COMPRESS_OFFLINE = True

try:
    # Test is DATA_MANAGER_ADMIN was already defined by PROJECT settings.
    DATA_MANAGER_ADMIN
except NameError:
    DATA_MANAGER_ADMIN = False

# Template configuration

from django.conf import global_settings

# Removed due to this: https://stackoverflow.com/a/39315587 - RDH (WCOA) 7/8/2019
# # RDH (MARCO) 20191114 - if tuple, make into a list
# TEMPLATE_CONTEXT_PROCESSORS = [x for x in global_settings.TEMPLATE_CONTEXT_PROCESSORS] + [
#     'django.core.context_processors.request',
#     'social_django.context_processors.backends',
#     'portal.base.context_processors.search_disabled',
# ]
#
# TEMPLATE_LOADERS = [x for x in global_settings.TEMPLATE_LOADERS] + [
#     'apptemplates.Loader',
# ]

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

try:
    FEEDBACK_IFRAME_URL
except NameError as e:
    FEEDBACK_IFRAME_URL = "//docs.google.com/forms/d/e/1FAIpQLSdi0nBoQK-3ia8rKtzh7cif0slzDCjA_ACH9Y_ryam-co6p8A/viewform?usp=sf_link"

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
SUPPORT_INVERTED_COORDINATES = True

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

SOCIAL_AUTH_JSONFIELD_ENABLED = True

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
    # 'accounts.pipeline.confirm_account',

    # Send a validation email to the user to verify its email address.
    'social.pipeline.mail.mail_validation',

    # Associates the current social details with another user account with
    # a similar email address. Disabled by default.
    # 'social.pipeline.social_auth.associate_by_email',

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
EMAIL_PORT = email_cfg.getint('PORT', 25)
if cfg.has_option('EMAIL', 'HOST_USER') and \
        cfg.has_option('EMAIL', 'HOST_PASSWORD'):
    EMAIL_HOST_USER = email_cfg.get('HOST_USER')
    EMAIL_HOST_PASSWORD = email_cfg.get('HOST_PASSWORD')
else:
    EMAIL_HOST_USER = ''
    EMAIL_HOST_PASSWORD = ''

EMAIL_BACKEND = email_cfg.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')

DEFAULT_FROM_EMAIL = email_cfg.get('DEFAULT_FROM_EMAIL', "MARCO Portal Team <portal@midatlanticocean.org>")
SERVER_EMAIL = email_cfg.get('SERVER_EMAIL', "MARCO Site Errors <ksdev@ecotrust.org>")
EMAIL_USE_TLS = email_cfg.getboolean('EMAIL_USE_TLS', False)
# for mail to admins/managers only
EMAIL_SUBJECT_PREFIX = app_cfg.get('EMAIL_SUBJECT_PREFIX', '[MARCO]') + ' '

if 'AWS' not in cfg.sections():
    cfg['AWS'] = {}

aws_cfg = cfg['AWS']

AWS_ACCESS_KEY_ID = aws_cfg.get('AWS_ACCESS_KEY_ID','')
AWS_SECRET_ACCESS_KEY = aws_cfg.get('AWS_SECRET_ACCESS_KEY','')
AWS_SES_REGION_NAME = aws_cfg.get('AWS_SES_REGION_NAME', 'us-east-1')
AWS_SES_REGION_ENDPOINT = aws_cfg.get('AWS_SES_REGION_ENDPOINT','email.us-east-1.amazonaws.com')


if 'CELERY' not in cfg.sections():
    cfg['CELERY'] = {}

celery_cfg = cfg['CELERY']

CELERY_RESULT_BACKEND = celery_cfg.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379')
BROKER_URL = celery_cfg.get('BROKER_URL', 'redis://localhost:6379/0')
CELERY_BROKER_URL = celery_cfg.get('CELERY_BROKER_URL', 'redis://localhost:6379')
CELERY_ALWAYS_EAGER = celery_cfg.get('CELERY_ALWAYS_EAGER', False)
CELERY_DISABLE_RATE_LIMITS = celery_cfg.get('CELERY_DISABLE_RATE_LIMITS', True)

GA_ACCOUNT = app_cfg.get('GA_ACCOUNT', '')

ADMINS = (('KSDev', 'ksdev@ecotrust.org'),)

NOCAPTCHA = True
RECAPTCHA_PUBLIC_KEY = app_cfg.get('RECAPTCHA_PUBLIC_KEY', '')
RECAPTCHA_PRIVATE_KEY = app_cfg.get('RECAPTCHA_PRIVATE_KEY','')

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

MAP_LIBRARY = app_cfg.get('MAP_LIBRARY', 'ol6')

if 'REGION' not in cfg.sections():
    cfg['REGION'] = {}

region_cfg = cfg['REGION']

try:
    # Test is PROJECT_REGION was already defined by PROJECT settings.
    PROJECT_REGION
except NameError:
    PROJECT_REGION = {}

PROJECT_REGION = {
    'name': region_cfg.get('NAME', PROJECT_REGION['name'] if PROJECT_REGION and 'name' in PROJECT_REGION.keys() else 'Mid-Atlantic Ocean'),
    'init_zoom': region_cfg.getint('INIT_ZOOM', PROJECT_REGION['init_zoom'] if PROJECT_REGION and 'init_zoom' in PROJECT_REGION.keys() else 7),
    'init_lat': region_cfg.getint('INIT_LAT', PROJECT_REGION['init_lat'] if PROJECT_REGION and 'init_lat' in PROJECT_REGION.keys() else 39),
    'init_lon': region_cfg.getint('INIT_LON', PROJECT_REGION['init_lon'] if PROJECT_REGION and 'init_lon' in PROJECT_REGION.keys() else -74),
    'srid': region_cfg.getint('SRID', PROJECT_REGION['srid'] if PROJECT_REGION and 'srid' in PROJECT_REGION.keys() else 4326),
    'map': region_cfg.get('MAP', PROJECT_REGION['map'] if PROJECT_REGION and 'map' in PROJECT_REGION.keys() else 'ocean'),
    'max_zoom': region_cfg.getint('MAX_ZOOM', PROJECT_REGION['max_zoom'] if PROJECT_REGION and 'max_zoom' in PROJECT_REGION.keys() else 13),
}

PROJECT_APP = app_cfg.get('PROJECT_APP', False)
if PROJECT_APP and not PROJECT_APP == 'False':
    INSTALLED_APPS.append(PROJECT_APP)

PROJECT_SETTINGS_FILE = app_cfg.get('PROJECT_SETTINGS_FILE', False)
if PROJECT_SETTINGS_FILE and not PROJECT_SETTINGS_FILE == 'False':
    try:
        from importlib import import_module
        APP_MODULE = import_module(PROJECT_APP)
        exec("from %s.settings import *" % APP_MODULE.__package__)
    except Exception as e:
        print(e)
        print('PROJECT APP (%s) settings not imported' % PROJECT_APP)

ADDITIONAL_APPS = app_cfg.get('ADDITIONAL_APPS', [])

INSTALLED_APPS += ADDITIONAL_APPS

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

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
