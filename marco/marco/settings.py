"""
Django settings for the Madrona Portal project.

References:
  https://docs.djangoproject.com/en/4.2/topics/settings/
  https://docs.djangoproject.com/en/4.2/ref/settings/

Requires: Django 4.2+, Wagtail 7.0+, Python 3.10+

Secret / credential precedence (highest → lowest):
  1. Environment variable  (e.g. export SECRET_KEY=...)
  2. config.ini value      (e.g. [APP]\nSECRET_KEY = ...)
  3. Hard-coded default    (safe defaults only — never real secrets)
"""
import ast
import json
import os
import configparser
from os.path import abspath, dirname
from typing import Any

# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------
PROJECT_ROOT = dirname(dirname(dirname(abspath(__file__))))
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

ASSETS_DIR = os.path.realpath(os.path.join(BASE_DIR, '..', 'assets'))
COMPONENTS_DIR = os.path.realpath(os.path.join(BASE_DIR, '..', 'bower_components'))
STYLES_DIR = os.path.realpath(os.path.join(ASSETS_DIR, 'styles'))

# ---------------------------------------------------------------------------
# Configuration file
# ---------------------------------------------------------------------------
MP_PROJECT_CONFIG = os.environ.get("MP_PROJECT_CONFIG", "config.ini")
CONFIG_FILE = os.path.normpath(os.path.join(BASE_DIR, MP_PROJECT_CONFIG))

cfg = configparser.ConfigParser()
cfg.read(CONFIG_FILE)

for section in ('APP', 'CATALOG', 'DATABASE', 'CACHES', 'CELERY', 'EMAIL', 'AWS', 'SOCIAL_AUTH', 'REGION'):
    if section not in cfg.sections():
        cfg[section] = {}

app_cfg = cfg['APP']
catalog_cfg = cfg['CATALOG']
db_cfg = cfg['DATABASE']
cache_cfg = cfg['CACHES']
celery_cfg = cfg['CELERY']
email_cfg = cfg['EMAIL']
aws_cfg = cfg['AWS']
social_cfg = cfg['SOCIAL_AUTH']
region_cfg = cfg['REGION']

# ---------------------------------------------------------------------------
# Secret resolution helper
# ---------------------------------------------------------------------------
def _env(env_key: str, cfg_section: configparser.SectionProxy, cfg_key: str,
         default: Any = '') -> str:
    """Return a setting value, checking the environment first.

    Priority: env var > config.ini > default.
    This allows Docker / CI to override secrets without touching config files.
    """
    return os.environ.get(env_key) or cfg_section.get(cfg_key, default)

# ---------------------------------------------------------------------------
# Core settings
# ---------------------------------------------------------------------------
DEBUG = app_cfg.getboolean('DEBUG', False)

APP_NAME = app_cfg.get('APP_NAME', 'Marine Planner')
APP_URL = app_cfg.get('APP_URL', '')
APP_TEAM_NAME = app_cfg.get('APP_TEAM_NAME', f"{APP_NAME} Team")

# env var takes priority so Docker / CI can inject secrets without touching config.ini
SECRET_KEY = _env('SECRET_KEY', app_cfg, 'SECRET_KEY', '')
_placeholder_phrases = ('forgot', 'change me', 'changeme', 'placeholder', 'you forgot')
if not SECRET_KEY or any(p in SECRET_KEY.lower() for p in _placeholder_phrases):
    raise RuntimeError(
        "SECRET_KEY is not set or still contains a placeholder value.\n"
        "Set it via the SECRET_KEY environment variable or in config.ini [APP].\n"
        f"Current value: {SECRET_KEY!r}"
    )

# ALLOWED_HOSTS: accepts a comma-separated string, a JSON array string, or a plain string.
def _parse_hosts(raw: str | None) -> list[str]:
    if not raw:
        return []
    raw = raw.strip()
    if raw.startswith('['):
        try:
            parsed = ast.literal_eval(raw)
            if isinstance(parsed, (list, tuple)):
                return [str(h).strip() for h in parsed if str(h).strip()]
        except (SyntaxError, ValueError):
            pass
        # Fall back: strip brackets and split on comma
        return [h.strip() for h in raw[1:-1].split(',') if h.strip()]
    if ',' in raw:
        return [h.strip() for h in raw.split(',') if h.strip()]
    return [raw]

_raw_hosts = os.environ.get('ALLOWED_HOSTS', app_cfg.get('ALLOWED_HOSTS', ''))
ALLOWED_HOSTS = _parse_hosts(_raw_hosts)

# Normalise bracketed IPv6 forms like [::1] → ::1 for Django host checks
ALLOWED_HOSTS = [
    h[1:-1] if h.startswith('[') and h.endswith(']') and ':' in h else h
    for h in ALLOWED_HOSTS
]

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
from django.utils.log import DEFAULT_LOGGING
LOGGING = DEFAULT_LOGGING
LOGGING['handlers']['mail_admins']['include_html'] = True

# ---------------------------------------------------------------------------
# Catalog settings
# ---------------------------------------------------------------------------
DATA_CATALOG_ENABLED = catalog_cfg.getboolean('DATA_CATALOG_ENABLED', True)
# Options: 'default' (built-in) or 'GeoPortal2'
CATALOG_TECHNOLOGY = catalog_cfg.get('CATALOG_TECHNOLOGY', 'default')
CATALOG_PROXY = catalog_cfg.get('CATALOG_PROXY', '')
CATALOG_SOURCE = catalog_cfg.get('CATALOG_SOURCE', 'http://127.0.0.1:9200')
CATALOG_QUERY_ENDPOINT = catalog_cfg.get(
    'CATALOG_QUERY_ENDPOINT',
    '/geoportal/elastic/metadata/item/_search/',
)

# ---------------------------------------------------------------------------
# Installed Applications  (Wagtail 7+)
# ---------------------------------------------------------------------------
import wagtail
WAGTAIL_VERSION = wagtail.VERSION[0]

INSTALLED_APPS = [
    # Wagtail contrib modules
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.contrib.sitemaps',
    'wagtail.contrib.styleguide',
    'wagtail.contrib.table_block',
    # Wagtail core
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail',

    # Portal application
    'marco_site',
    'marco.apps.MadronaPortalConfig',

    # Django Autocomplete Light
    'dal',
    'dal_select2',
    'dal_queryset_sequence',

    # Django core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.gis',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Third-party
    'django_redis',
    'email_log',
    'djcelery_email',
    'compressor',
    'taggit',
    'modelcluster',
    # rpc4django removed — replaced by DRF API views (visualize/api.py, drawing/api.py, mapgroups/api.py)
    'tinymce',
    'django_recaptcha',        # Wagtail 7+ uses django-recaptcha v4 (app name: django_recaptcha)
    'social_django',
    'flatblocks',
    'import_export',
    'rest_framework',

    # Portal sub-apps
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

    # Ecotrust / Madrona sub-apps
    'data_manager',
    'layers',
    'url_short',
    'visualize',
    'features',
    'scenarios',
    'drawing',
    'manipulators',
    'explore',
    'accounts.apps.AccountsAppConfig',
    'django_social_share',
    'mapgroups',
    'survey',
]

# Optional apps — installed when available
for _optional_app in ('nested_admin', 'colorfield', 'wagtailcharts'):
    try:
        __import__(_optional_app)
        if _optional_app not in INSTALLED_APPS:
            INSTALLED_APPS.append(_optional_app)
    except ImportError:
        pass

# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------
MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'marco.host_site_middleware.HostSiteMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
]

X_FRAME_OPTIONS = 'SAMEORIGIN'

# ---------------------------------------------------------------------------
# URLs / WSGI
# ---------------------------------------------------------------------------
SITE_ID = 1
INTERNAL_IPS = ('127.0.0.1',)
ROOT_URLCONF = 'marco.urls'
WSGI_APPLICATION = 'marco.wsgi.application'
APPEND_SLASH=True

# ---------------------------------------------------------------------------
# Database (PostGIS by default)
# Env var overrides (Docker / CI): DB_ENGINE, DB_NAME, DB_USER, DB_PASSWORD,
# DB_HOST, DB_PORT.  SQL_* aliases are also accepted for legacy docker-compose
# compatibility.
# ---------------------------------------------------------------------------
_db_engine = (
    os.environ.get('DB_ENGINE')
    or os.environ.get('SQL_ENGINE')
    or db_cfg.get('ENGINE', 'django.contrib.gis.db.backends.postgis')
)
default_db: dict[str, Any] = {'ENGINE': _db_engine}

if _db_engine.endswith('spatialite'):
    default_db['SPATIALITE_LIBRARY_PATH'] = db_cfg.get('SPATIALITE_LIBRARY_PATH')
    default_db['NAME'] = (
        os.environ.get('DB_NAME')
        or db_cfg.get('NAME', os.path.join(BASE_DIR, 'marco.db'))
    )
else:
    default_db['NAME'] = (
        os.environ.get('DB_NAME') or os.environ.get('SQL_DATABASE')
        or db_cfg.get('NAME', '')
    )
    default_db['USER'] = (
        os.environ.get('DB_USER') or os.environ.get('SQL_USER')
        or db_cfg.get('USER', '')
    )
    default_db['PASSWORD'] = (
        os.environ.get('DB_PASSWORD') or os.environ.get('SQL_PASSWORD')
        or db_cfg.get('PASSWORD', '')
    )
    default_db['HOST'] = (
        os.environ.get('DB_HOST') or os.environ.get('SQL_HOST')
        or db_cfg.get('HOST', 'localhost')
    )
    default_db['PORT'] = int(
        os.environ.get('DB_PORT') or os.environ.get('SQL_PORT')
        or db_cfg.get('PORT', '5432')
    )

DATABASES = {'default': default_db}
DB_CHANNEL = db_cfg.get('DB_CHANNEL', 'madrona-portal')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---------------------------------------------------------------------------
# Caching (Redis via django-redis)
# Env var override: REDIS_URL (e.g. redis://:password@tasks:6379/1)
# ---------------------------------------------------------------------------
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

_redis_location = (
    os.environ.get('REDIS_URL')
    or cache_cfg.get('LOCATION', 'redis://127.0.0.1:6379/1')
)

CACHES = {
    'default': {
        'BACKEND': cache_cfg.get('BACKEND', 'django_redis.cache.RedisCache'),
        'LOCATION': _redis_location,
        'KEY_PREFIX': 'marco_portal',
        'OPTIONS': {
            'CLIENT_CLASS': cache_cfg.get('CLIENT_CLASS', 'django_redis.client.DefaultClient'),
        },
    }
}

# ---------------------------------------------------------------------------
# Internationalisation
# ---------------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = app_cfg.get('TIME_ZONE', 'UTC')
USE_I18N = True
USE_TZ = True
WAGTAIL_I18N_ENABLED = False
WAGTAIL_CONTENT_LANGUAGES = LANGUAGES = [('en', "English")]

# ---------------------------------------------------------------------------
# Static & media files
# ---------------------------------------------------------------------------
STATIC_ROOT = _env('STATIC_ROOT', app_cfg, 'STATIC_ROOT', os.path.join(BASE_DIR, 'static'))
STATIC_URL = _env('STATIC_URL', app_cfg, 'STATIC_URL', '/static/')
STATIC_CORE = app_cfg.get('STATIC_CORE', '')

MEDIA_ROOT = _env('MEDIA_ROOT', app_cfg, 'MEDIA_ROOT', os.path.join(BASE_DIR, 'media'))
MEDIA_URL = _env('MEDIA_URL', app_cfg, 'MEDIA_URL', '/media/')

_static_root_abs = os.path.abspath(STATIC_ROOT)
_staticfiles_dirs: list[str] = []
for _dir in (STYLES_DIR, COMPONENTS_DIR, ASSETS_DIR, STATIC_CORE):
    if not _dir:
        continue
    _abs = os.path.abspath(_dir)
    if _abs == _static_root_abs or _abs in [os.path.abspath(d) for d in _staticfiles_dirs]:
        continue
    _staticfiles_dirs.append(_dir)

STATICFILES_DIRS = tuple(_staticfiles_dirs)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'compressor.finders.CompressorFinder',
)

# Django Compressor / SASS
COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)
COMPRESS_ENABLED = app_cfg.getboolean('COMPRESS_ENABLED', True)
COMPRESS_OFFLINE = True

# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------
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
                'django.contrib.messages.context_processors.messages',
            ]
        },
    },
]

# ---------------------------------------------------------------------------
# Wagtail
# ---------------------------------------------------------------------------
LOGIN_URL = 'account:index'
WAGTAIL_SITE_NAME = 'MARCO Portal'
WAGTAILSEARCH_RESULTS_TEMPLATE = 'portal/search_results.html'
WAGTAILIMAGES_FEATURE_DETECTION_ENABLED = False
WAGTAILIMAGES_IMAGE_MODEL = 'base.PortalImage'

# ---------------------------------------------------------------------------
# Map / Geospatial
# ---------------------------------------------------------------------------
MAP_LIBRARY = app_cfg.get('MAP_LIBRARY', 'ol6')
GEOMETRY_DB_SRID = 3857
GEOMETRY_CLIENT_SRID = 3857
GEOJSON_SRID = 3857
GEOJSON_DOWNLOAD = True
SUPPORT_INVERTED_COORDINATES = False
SERVER_SRID = 4326

KML_SIMPLIFY_TOLERANCE = 20           # metres
KML_SIMPLIFY_TOLERANCE_DEGREES = 0.0002
KML_EXTRUDE_HEIGHT = 100
KML_ALTITUDEMODE_DEFAULT = 'absolute'

LAYER_TYPE_CHOICES = (
    ('XYZ', 'XYZ'),
    ('WMS', 'WMS'),
    ('ArcRest', 'ArcRest'),
    ('ArcFeatureServer', 'ArcFeatureServer'),
    ('radio', 'radio'),
    ('checkbox', 'checkbox'),
    ('Vector', 'Vector'),
    ('VectorTile', 'VectorTile'),
    ('placeholder', 'placeholder'),
)

# Region defaults (can be overridden by PROJECT settings or config.ini)
PROJECT_REGION: dict = {}
PROJECT_REGION = {
    'name':      region_cfg.get('NAME',      PROJECT_REGION.get('name',      'Mid-Atlantic Ocean')),
    'init_zoom': region_cfg.getint('INIT_ZOOM', PROJECT_REGION.get('init_zoom', 7)),
    'init_lat':  region_cfg.getfloat('INIT_LAT',  PROJECT_REGION.get('init_lat',  39.0)),
    'init_lon':  region_cfg.getfloat('INIT_LON',  PROJECT_REGION.get('init_lon',  -74.0)),
    'srid':      region_cfg.getint('SRID',      PROJECT_REGION.get('srid',      4326)),
    'map':       region_cfg.get('MAP',          PROJECT_REGION.get('map',       'ocean')),
    'max_zoom':  region_cfg.getint('MAX_ZOOM',  PROJECT_REGION.get('max_zoom',  13)),
}

# WMS proxy settings
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

# ---------------------------------------------------------------------------
# Sharing / features
# ---------------------------------------------------------------------------
DATA_MANAGER_ADMIN = False
SHARING_TO_PUBLIC_GROUPS = ['Share with Public']
SHARING_TO_STAFF_GROUPS = ['Share with Staff']
FEEDBACK_IFRAME_URL = (
    "//docs.google.com/forms/d/e/"
    "1FAIpQLSdi0nBoQK-3ia8rKtzh7cif0slzDCjA_ACH9Y_ryam-co6p8A/viewform?usp=sf_link"
)
DISCLAIMER_BUTTON_DEFAULT = False

# ---------------------------------------------------------------------------
# Social Authentication
# ---------------------------------------------------------------------------
SOCIAL_AUTH_NEW_USER_URL = '/account/?new=true&login=django'
SOCIAL_AUTH_FACEBOOK_NEW_USER_URL = '/account/?new=true&login=facebook'
SOCIAL_AUTH_TWITTER_NEW_USER_URL = '/account/?new=true&login=twitter'
SOCIAL_AUTH_GOOGLE_NEW_USER_URL = '/account/?new=true&login=google'

SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/account/?login=django'
SOCIAL_AUTH_FACEBOOK_LOGIN_REDIRECT_URL = '/account/?login=facebook'
SOCIAL_AUTH_TWITTER_LOGIN_REDIRECT_URL = '/account/?login=twitter'
SOCIAL_AUTH_GOOGLE_LOGIN_REDIRECT_URL = '/account/?login=google'

# Env var overrides: FACEBOOK_KEY, FACEBOOK_SECRET, TWITTER_KEY,
#                    TWITTER_SECRET, GOOGLE_KEY, GOOGLE_SECRET
SOCIAL_AUTH_FACEBOOK_KEY = _env('FACEBOOK_KEY', social_cfg, 'FACEBOOK_KEY', '')
SOCIAL_AUTH_FACEBOOK_SECRET = _env('FACEBOOK_SECRET', social_cfg, 'FACEBOOK_SECRET', '')
SOCIAL_AUTH_FACEBOOK_SCOPE = ['public_profile,email']

SOCIAL_AUTH_TWITTER_KEY = _env('TWITTER_KEY', social_cfg, 'TWITTER_KEY', '')
SOCIAL_AUTH_TWITTER_SECRET = _env('TWITTER_SECRET', social_cfg, 'TWITTER_SECRET', '')

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = _env('GOOGLE_KEY', social_cfg, 'GOOGLE_KEY', '')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = _env('GOOGLE_SECRET', social_cfg, 'GOOGLE_SECRET', '')

SOCIAL_AUTH_DISCONNECT_REDIRECT_URL = '/'
SOCIAL_AUTH_JSONFIELD_ENABLED = True
SOCIAL_AUTH_EMAIL_VALIDATION_FUNCTION = 'accounts.pipeline.send_validation_email'
SOCIAL_AUTH_EMAIL_VALIDATION_URL = '/account/validate'

SOCIAL_AUTH_PIPELINE = (
    'accounts.pipeline.clean_session',
    # social-auth-core pipeline steps (social_core.pipeline.*)
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.mail.mail_validation',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
    'accounts.pipeline.set_user_permissions',
    'accounts.pipeline.get_social_details',
    'accounts.pipeline.clean_session',
)

# ---------------------------------------------------------------------------
# Email
# Env var overrides: EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER,
#                    EMAIL_HOST_PASSWORD, EMAIL_USE_TLS
# ---------------------------------------------------------------------------
EMAIL_HOST = _env('EMAIL_HOST', email_cfg, 'HOST', 'localhost')
EMAIL_PORT = int(_env('EMAIL_PORT', email_cfg, 'PORT', '25'))
EMAIL_HOST_USER = _env('EMAIL_HOST_USER', email_cfg, 'HOST_USER', '')
EMAIL_HOST_PASSWORD = _env('EMAIL_HOST_PASSWORD', email_cfg, 'HOST_PASSWORD', '')
EMAIL_BACKEND = email_cfg.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
DEFAULT_FROM_EMAIL = email_cfg.get('DEFAULT_FROM_EMAIL', "MARCO Portal Team <portal@midatlanticocean.org>")
SERVER_EMAIL = email_cfg.get('SERVER_EMAIL', "MARCO Site Errors <ksdev@ecotrust.org>")
EMAIL_USE_TLS = bool(os.environ.get('EMAIL_USE_TLS', email_cfg.get('EMAIL_USE_TLS', 'false')).lower() in ('1', 'true', 'yes'))
EMAIL_SUBJECT_PREFIX = app_cfg.get('EMAIL_SUBJECT_PREFIX', '[MARCO]') + ' '

ADMINS = (('KSDev', 'ksdev@ecotrust.org'),)

# ---------------------------------------------------------------------------
# AWS (SES)
# Env var overrides: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,
#                    AWS_SES_REGION_NAME, AWS_SES_REGION_ENDPOINT
# ---------------------------------------------------------------------------
AWS_ACCESS_KEY_ID = _env('AWS_ACCESS_KEY_ID', aws_cfg, 'AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = _env('AWS_SECRET_ACCESS_KEY', aws_cfg, 'AWS_SECRET_ACCESS_KEY', '')
AWS_SES_REGION_NAME = _env('AWS_SES_REGION_NAME', aws_cfg, 'AWS_SES_REGION_NAME', 'us-east-1')
AWS_SES_REGION_ENDPOINT = _env('AWS_SES_REGION_ENDPOINT', aws_cfg, 'AWS_SES_REGION_ENDPOINT', 'email.us-east-1.amazonaws.com')

# ---------------------------------------------------------------------------
# Celery (Celery 5+ settings)
# Env var overrides: CELERY_BROKER_URL, CELERY_RESULT_BACKEND
# ---------------------------------------------------------------------------
CELERY_BROKER_URL = (
    os.environ.get('CELERY_BROKER_URL')
    or os.environ.get('REDIS_URL')
    or celery_cfg.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
)
CELERY_RESULT_BACKEND = (
    os.environ.get('CELERY_RESULT_BACKEND')
    or os.environ.get('REDIS_URL')
    or celery_cfg.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379')
)
CELERY_TASK_ALWAYS_EAGER = celery_cfg.getboolean('CELERY_ALWAYS_EAGER', False)
CELERY_TASK_RATE_LIMITS_DISABLED = celery_cfg.getboolean('CELERY_DISABLE_RATE_LIMITS', True)

# ---------------------------------------------------------------------------
# ReCAPTCHA
# ---------------------------------------------------------------------------
NOCAPTCHA = True
RECAPTCHA_PUBLIC_KEY = _env('RECAPTCHA_PUBLIC_KEY', app_cfg, 'RECAPTCHA_PUBLIC_KEY', '')
RECAPTCHA_PRIVATE_KEY = _env('RECAPTCHA_PRIVATE_KEY', app_cfg, 'RECAPTCHA_PRIVATE_KEY', '')

# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------
GA_ACCOUNT = app_cfg.get('GA_ACCOUNT', '')

# ---------------------------------------------------------------------------
# Project-level settings overrides
# (Optional app + settings file specified in config.ini)
# ---------------------------------------------------------------------------
PROJECT_APP = app_cfg.get('PROJECT_APP', '')
if PROJECT_APP:
    INSTALLED_APPS.append(PROJECT_APP)

if 'visualize' in INSTALLED_APPS:
    from visualize.settings import *  # noqa: F401, F403
if 'data_manager' in INSTALLED_APPS:
    from data_manager.settings import *  # noqa: F401, F403

PROJECT_SETTINGS_FILE = app_cfg.get('PROJECT_SETTINGS_FILE', '')
if PROJECT_SETTINGS_FILE:
    try:
        from importlib import import_module
        _project_module = import_module(PROJECT_APP)
        _settings_module = import_module(f"{_project_module.__package__}.settings")
        # Merge all public names into the current module's namespace
        for _k, _v in vars(_settings_module).items():
            if not _k.startswith('_'):
                globals()[_k] = _v
    except Exception as _e:
        import warnings
        warnings.warn(f"PROJECT APP ({PROJECT_APP}) settings not imported: {_e}")

# ADDITIONAL_APPS / ADDITIONAL_MIDDLEWARE — expected as JSON arrays in config.ini
# e.g.: ADDITIONAL_APPS = ["my_custom_app"]
def _parse_list_setting(raw: str) -> list:
    """Safely parse a JSON or Python list literal from a config value."""
    if not raw:
        return []
    try:
        result = json.loads(raw)
        if isinstance(result, list):
            return result
    except (json.JSONDecodeError, TypeError):
        pass
    try:
        result = ast.literal_eval(raw)
        if isinstance(result, list):
            return result
    except (SyntaxError, ValueError):
        pass
    return []

ADDITIONAL_APPS = _parse_list_setting(app_cfg.get('ADDITIONAL_APPS', ''))
ADDITIONAL_MIDDLEWARE = _parse_list_setting(app_cfg.get('ADDITIONAL_MIDDLEWARE', ''))

INSTALLED_APPS += ADDITIONAL_APPS
MIDDLEWARE += ADDITIONAL_MIDDLEWARE
