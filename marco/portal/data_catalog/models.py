from django.conf import settings

if settings.WAGTAIL_VERSION > 3:
    from wagtail.models import Page
elif settings.WAGTAIL_VERSION > 1:
    from wagtail.core.models import Page
else:
    from wagtail.core.models import Page


from portal.base.models import PageBase
from .views import theme_query

class DataCatalog(PageBase):
    subpage_types = []

    def get_context(self, request, *args, **kwargs):
    	return {
    		'self': self,
    		'request': request,
    		'themes': theme_query()
    	}
