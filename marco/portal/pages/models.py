from django.db import models
from django.conf import settings
from wagtail.contrib.table_block.blocks import TableBlock

if settings.WAGTAIL_VERSION > 3:
    from wagtail import blocks
    from wagtail.fields import RichTextField, StreamField
    from wagtail.admin.panels import FieldPanel
    from wagtail.search import index
elif settings.WAGTAIL_VERSION > 1:
    from wagtail.core import blocks
    from wagtail.core.fields import RichTextField, StreamField
    from wagtail.admin.edit_handlers import FieldPanel
    from wagtail.search import index
else:
    from wagtail.core import blocks
    from wagtail.core.fields import RichTextField
    from wagtail.admin.edit_handlers import FieldPanel
    from wagtail.search import index

from portal.base.models import PageBase

class PageTableBlock(blocks.StreamBlock):
    # https://docs.wagtail.org/en/stable/reference/contrib/table_block.html
    table = TableBlock(table_options={
        'renderer': 'html',
    })

class Page(PageBase):

    if settings.WAGTAIL_VERSION > 3:
        body = StreamField(
            [
                ('text', blocks.RichTextBlock()),
                ('table', PageTableBlock()),
            ], 
            blank=True, 
            null=True, 
            default=None,
            use_json_field=True,
        )
    else:
        body = StreamField(
            [
                ('text', blocks.RichTextBlock()),
                ('table', PageTableBlock()),
            ], 
            blank=True, 
            null=True, 
            default=None,
        )

    # search_fields = PageBase.search_fields + [
    #     index.SearchField('body'),
    # ]
    content_panels = PageBase.content_panels + [
        FieldPanel('body', classname="full"),
    ]
