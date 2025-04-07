from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

if settings.WAGTAIL_VERSION > 1:
    from wagtail.models import Page
else:
    from wagtail.models import Page


from portal.base.models import PageBase
from .views import theme_query

class DataCatalog(PageBase):
    subpage_types = []

    def get_context(self, request, *args, **kwargs):
        site = get_current_site(request)
        return {
            'self': self,
            'request': request,
            'themes': theme_query(site=site)
        }
