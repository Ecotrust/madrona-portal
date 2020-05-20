from django.db import models
from django.conf import settings

if settings.WAGTAIL_VERSION > 1:
    from wagtail.admin.edit_handlers import FieldPanel
    from wagtail.search import index
else:
    from wagtail.wagtailadmin.edit_handlers import FieldPanel
    from wagtail.wagtailsearch import index

from portal.base.models import PageBase,DetailPageBase

class DataGaps(PageBase):
    subpage_types = ['DataGap']

    def get_detail_children(self):
        return DataGap.objects.child_of(self)

class DataGap(DetailPageBase):
    parent_page_types = ['DataGaps']

    target_year = models.CharField(max_length=4)

    search_fields = DetailPageBase.search_fields + (
        index.SearchField('title'),
        index.SearchField('description'),
        index.FilterField('target_year'),
    )

    content_panels = DetailPageBase.content_panels + [
        FieldPanel('target_year'),
    ]
