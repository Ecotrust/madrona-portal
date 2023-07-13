from django.db import models
from modelcluster.fields import ParentalKey
from django.conf import settings

if settings.WAGTAIL_VERSION > 1:
    from wagtail.admin.panels import FieldPanel, InlinePanel, \
        MultiFieldPanel,TitleFieldPanel
    from wagtail.fields import RichTextField
    from wagtail.models import Orderable
    from wagtail.search import index
else:
    from wagtail.admin.panels import FieldPanel, InlinePanel, \
        MultiFieldPanel
    from wagtail.fields import RichTextField
    from wagtail.models import Orderable
    from wagtail.search import index

from portal.base.models import PageBase, DetailPageBase, MediaItem

from accounts.forms import SignUpForm


# The abstract model for ocean story sections, complete with panels
class GridPageSectionBase(MediaItem):
    title = models.CharField(max_length=255, blank=True)
    body = RichTextField(blank=True)

    panels = [
        TitleFieldPanel('title'),
        MultiFieldPanel(MediaItem.panels, "media"),
        FieldPanel('body', classname="full"),
    ]

    index_fields = MediaItem.index_fields + (
        'title',
        'body',
    )

    class Meta:
        abstract = True

class GridPageSection(Orderable, GridPageSectionBase):
    page = ParentalKey('GridPageDetail', related_name='sections')



class GridPage(PageBase):
    subpage_types = ['GridPageDetail']

    search_fields = (index.SearchField('description'),)

    def get_detail_children(self):
        return GridPageDetail.objects.child_of(self)

    def get_context(self, request, *args, **kwargs):
        return {
            'self': self,
            'request': request,
            'form': SignUpForm()
        }


class GridPageDetail(DetailPageBase):
    parent_page_types = ['GridPage']

    metric = models.CharField(max_length=4, blank=True, null=True)

    search_fields = DetailPageBase.search_fields + (
        index.SearchField('description'),
        index.FilterField('metric'),
    )

    content_panels = DetailPageBase.content_panels + [
        FieldPanel('metric'),
    ]
GridPageDetail.content_panels += [InlinePanel('sections', label="Sections"),]
