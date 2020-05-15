from django.db import models

from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.search import index

from portal.base.models import PageBase

class Page(PageBase):

    body = RichTextField()
    search_fields = PageBase.search_fields + [
        index.SearchField('body'),
    ]
    content_panels = PageBase.content_panels + [
        FieldPanel('body', classname="full"),
    ]
