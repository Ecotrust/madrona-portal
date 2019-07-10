from datetime import date

from django.db import models
from django.db.models import Q
from modelcluster.fields import ParentalKey
from wagtail.core.fields import RichTextField
from wagtail.core.models import Page, Orderable
from wagtail.images.edit_handlers import ImageChooserPanel

from wagtail.search import index
from wagtail.admin.edit_handlers import FieldPanel,MultiFieldPanel, \
    InlinePanel

from portal.base.models import MediaItem
from portal.base.models import PageBase, DetailPageBase

from portal.base.models import PortalImage

class StorySection(Orderable, MediaItem):
    page = ParentalKey('Story', related_name='story_sections')
    header = models.CharField(max_length=255, blank=True)
    body = RichTextField(blank=True)

    panels = [
        FieldPanel('header'),
        MultiFieldPanel(MediaItem.panels, "media"),
        FieldPanel('body', classname="full"),
    ]

class Story(Page):
    class Meta:
        ordering = ('-posted',)

    parent_page_types = ['News']

    posted = models.DateField(help_text=("Date story posted"))
    map_link = models.TextField(max_length=4096, blank=True, null=True,
                                help_text=("A Marine Planner map url, or blank "
                                           "if this story isn't connected to a "
                                           "map."))
    description = RichTextField(blank=True, null=True, help_text=("The "
        "article's introductory content. Text here appears in the list of news "
        "stories, as well as below the headline and above any section content "
        "in the story page."))
    feature_image = models.ForeignKey(
        PortalImage,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text=("Image displayed on the news story list.")
    )

    search_fields = (
        index.FilterField('latest_revision_created_at'),
        index.SearchField('title'),
        index.SearchField('description'),
    )
    content_panels = [
        MultiFieldPanel([
            FieldPanel('posted'),
            FieldPanel('map_link'),
            ImageChooserPanel('feature_image'),
            FieldPanel('title'),
            FieldPanel('description'),
        ], "News Story"),
    ]

# Inline panels have to be added after class definition, because foreign keys
# defined in other models aren't connected until after the model has been
# defined
Story.content_panels.append(InlinePanel('story_sections', label='Story Section'))

class News(PageBase):
    subpage_types = ['Story']

    def stories(self):
        # Get list of live event pages that are descendants of this page
        stories = Story.objects.live().child_of(self)
        stories = stories.order_by('-posted')

        return stories
