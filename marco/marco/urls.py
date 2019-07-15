import os

# from django.conf.urls import patterns, include, url
from django.urls import re_path, include, path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin

from django.views.generic.base import RedirectView, TemplateView

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.search import urls as wagtailsearch_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.core import urls as wagtail_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.images import urls as wagtailimages_urls

import mapgroups.urls
import accounts.urls
import explore.urls
# import wcoa

from rpc4django.views import serve_rpc_request
from social.apps import django_app
from portal.base import views as base_views
from portal.data_catalog import views as data_catalog_views
from marco_site import views as marco_site_views

admin.autodiscover()


# Register search signal handlers
from wagtail.search.signal_handlers import register_signal_handlers as wagtailsearch_register_signal_handlers
wagtailsearch_register_signal_handlers()

# if settings.PROJECT == 'WCOA":
    # import wcoa.urls

urlpatterns = [
    #'',
    re_path(r'^sitemap\.xml$', sitemap),

    path('django-admin/', admin.site.urls),

    re_path(r'^rpc$', serve_rpc_request),

    # path('wcoa/', include('wcoa.urls')),

    # https://github.com/omab/python-social-auth/issues/399
    # I want the psa urls to be inside the account urls, but PSA doesn't allow
    # nested namespaces. It will likely be fixed in 0.22
    re_path(r'^account/auth/', include('social.apps.django_app.urls'), name='social'),
    re_path(r'^account/', include('accounts.urls'), name='account'),
    re_path(r'^collaborate/groups/', include('mapgroups.urls'), name='groups'),
    re_path(r'^groups/', include('mapgroups.urls'), name='groups'),
    re_path(r'^g/', RedirectView.as_view(url='/groups/')), # 301

    re_path(r'^admin/', include(wagtailadmin_urls)),
    re_path(r'^search/', base_views.search),
    re_path(r'^documents/', include(wagtaildocs_urls)),

    # url(r'^data-catalog/', include('portal.data_catalog.urls')),
    re_path(r'^data-catalog/([A-Za-z0-9_-]+)/$', data_catalog_views.theme),
    re_path(r'^data-catalog/[A-Za-z0-9_-]*/', include('explore.urls')),
    re_path(r'^data_manager/', include('data_manager.urls')),
    re_path(r'^styleguide/$', marco_site_views.styleguide, name='styleguide'),
    re_path(r'^planner/', include('visualize.urls')),
    re_path(r'^embed/', include('visualize.urls')),
    re_path(r'^visualize/', include('visualize.urls')),
    re_path(r'^features/', include('features.urls')),
    re_path(r'^scenario/', include('scenarios.urls')),
    re_path(r'^drawing/', include('drawing.urls')),
    re_path(r'^proxy/', include('mp_proxy.urls')),

    re_path(r'^join/', RedirectView.as_view(url='/account/register/')),

    re_path(r'^images/', include(wagtailimages_urls)),
    re_path(r'', include(wagtail_urls)),
]


if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
