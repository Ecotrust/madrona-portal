from django.db import models
from django.conf import settings

if settings.WAGTAIL_VERSION > 1:
    from wagtail.core.fields import RichTextField
    from wagtail.admin.edit_handlers import FieldPanel
    from wagtail.search import index
else:
    from wagtail.wagtailcore.fields import RichTextField
    from wagtail.wagtailadmin.edit_handlers import FieldPanel
    from wagtail.wagtailsearch import index

from portal.base.models import PageBase

class Page(PageBase):

    body = RichTextField()
    search_fields = PageBase.search_fields + [
        index.SearchField('body'),
    ]
    content_panels = PageBase.content_panels + [
        FieldPanel('body', classname="full"),
    ]
