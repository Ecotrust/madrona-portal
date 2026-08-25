"""
URL configuration for the Madrona Portal project.

Requires: Django 4.2+, Wagtail 7.0+
"""
import warnings
from importlib import import_module
from importlib.util import find_spec

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, re_path
from django.views.generic.base import RedirectView

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail import urls as wagtail_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.images import urls as wagtailimages_urls
from wagtail.search.signal_handlers import register_signal_handlers as wagtailsearch_register_signal_handlers

import mapgroups.urls
import accounts.urls
import explore.urls

from marco.rpc_compat import rpc_view

from portal.base import views as base_views
from portal.data_catalog import views as data_catalog_views
from marco_site import views as marco_site_views

admin.autodiscover()
wagtailsearch_register_signal_handlers()


def _iter_discovered_api_includes():
    """Yield include() patterns for apps exposing urls.api_urlpatterns."""
    for installed_app in settings.INSTALLED_APPS:
        app_module = installed_app.split('.apps.', 1)[0]
        urls_module_name = f"{app_module}.urls"

        try:
            if find_spec(urls_module_name) is None:
                continue
        except (ImportError, ValueError, AttributeError):
            continue

        try:
            app_urls = import_module(urls_module_name)
        except Exception as exc:  # pragma: no cover - defensive runtime warning
            warnings.warn(f"Could not import '{urls_module_name}' for api_urlpatterns: {exc}")
            continue

        app_api_urlpatterns = getattr(app_urls, 'api_urlpatterns', None)
        if app_api_urlpatterns:
            yield re_path(r'^api/', include(app_api_urlpatterns))


api_url_includes = list(_iter_discovered_api_includes())

# ---------------------------------------------------------------------------
# Project-specific URL patterns
# Optional: a project app can prepend its own patterns.
# ---------------------------------------------------------------------------
urlpatterns: list = []

if settings.PROJECT_APP:
    try:
        portal_app_urls = import_module(f"{settings.PROJECT_APP}.urls")
        urlpatterns = list(getattr(portal_app_urls, 'urlpatterns', []))
    except (ImportError, AttributeError) as e:
        warnings.warn(f"Could not load URL patterns from PROJECT_APP '{settings.PROJECT_APP}': {e}")

# ---------------------------------------------------------------------------
# Core URL patterns
# ---------------------------------------------------------------------------
urlpatterns += [
    re_path(r'^sitemap\.xml$', sitemap),

    re_path(r'^django-admin/', admin.site.urls),
    re_path(r'^admin/', include(wagtailadmin_urls)),

    # /rpc — JSON-RPC 2.0 compat shim for legacy frontend JS (see rpc_compat.py)
    re_path(r'^rpc/', rpc_view),
]

urlpatterns += api_url_includes

urlpatterns += [
    # DRF REST replacements discovered from each sub-app's urls.py api_urlpatterns

    re_path(r'^auth/', include('social_django.urls', namespace='social')),
    re_path(r'^account/', include('accounts.urls'), name='account'),
    re_path(r'^collaborate/groups/', include('mapgroups.urls'), name='groups'),
    re_path(r'^groups/', include('mapgroups.urls'), name='groups'),
    re_path(r'^g/', RedirectView.as_view(url='/groups/')),   # 301 legacy redirect

    re_path(r'^search/', base_views.search),
    re_path(r'^documents/', include(wagtaildocs_urls)),
    re_path(r'^images/', include(wagtailimages_urls)),

    # Data catalog: named theme pages then the explore SPA
    # TODO (POR-206): Restrict theme slugs to prevent spaces and special characters.
    re_path(r'^data-catalog/([\w\-\s\(\)]+)/?$', data_catalog_views.theme, name="portal.data_catalog.views.theme"),
    re_path(r'^data-catalog/[\w\-\s\(\)]*/', include('explore.urls')),

    re_path(r'^data_manager/', include('layers.urls')),
    re_path(r'^old_manager/', include('data_manager.urls')),
    re_path(r'^url_shortener/', include('url_short.urls')),
    re_path(r'^layers/', include('layers.urls')),
    re_path(r'^styleguide/$', marco_site_views.styleguide, name='styleguide'),
    re_path(r'^planner/', include('visualize.urls')),
    re_path(r'^embed/', include('visualize.urls')),
    re_path(r'^visualize/', include('visualize.urls')),
    re_path(r'^features/', include('features.urls')),
    re_path(r'^scenario/', include('scenarios.urls')),
    re_path(r'^drawing/', include('drawing.urls')),
    re_path(r'^proxy/', include('mp_proxy.urls')),

    re_path(r'^join/', RedirectView.as_view(url='/account/register/')),  # 301 legacy redirect
]

# Optional survey module
if 'survey' in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path(r'^survey/', include('survey.urls', namespace='survey')),
    ]

# Custom 404 handler
if hasattr(settings, 'HANDLER_404'):
    handler404 = settings.HANDLER_404

# Development: serve static and media files through Django
if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Wagtail page routing — must be last
urlpatterns += [re_path(r'', include(wagtail_urls))]
