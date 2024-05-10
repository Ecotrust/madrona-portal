from django.db import models
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect

from modelcluster.fields import ParentalKey

from django.conf import settings

if settings.WAGTAIL_VERSION > 3:
    from wagtail.models import Orderable, Page
    from wagtail.fields import RichTextField
    from wagtail.search import index
    from wagtail.admin.panels import FieldPanel,InlinePanel,MultiFieldPanel,FieldRowPanel,PageChooserPanel,TitleFieldPanel
    from wagtail.images.models import Image
elif settings.WAGTAIL_VERSION > 1:
    from wagtail.models import Orderable, Page
    from wagtail.fields import RichTextField
    from wagtail.search import index
    from wagtail.admin.panels import FieldPanel,InlinePanel,MultiFieldPanel,FieldRowPanel,PageChooserPanel
    from wagtail.images.models import Image
    from wagtail.images.edit_handlers import ImageChooserPanel
    TitleFieldPanel = FieldPanel
else:
    from wagtail.models import Orderable, Page
    from wagtail.fields import RichTextField
    from wagtail.search import index
    from wagtail.admin.panels import FieldPanel,InlinePanel,MultiFieldPanel,FieldRowPanel,PageChooserPanel
    from wagtail.images.models import Image
    from wagtail.images.edit_handlers import ImageChooserPanel
    TitleFieldPanel = FieldPanel

from portal.ocean_stories.models import OceanStory

from portal.base.models import PortalImage

# The abstract model for related links, complete with panels
class HomePageCarouselSlide(models.Model):
    title = models.CharField(max_length=255, blank=True)
    body = RichTextField(blank=True, null=True)
    link_external = models.URLField("External link", blank=True)
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL,
    )

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        else:
            return self.link_external

    slide_image = models.ForeignKey(
        PortalImage,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    panels = [
        TitleFieldPanel('title'),
        FieldPanel('body'),
        FieldPanel('link_external'),
        PageChooserPanel('link_page'),
        FieldPanel('slide_image'),
    ]

    class Meta:
        abstract = True

# The real home page model which combines:
  # the abstract model
  # an Orderable helper class
  # what amounts to a ForeignKey link to the home page model
class HomePageCarousel(Orderable, HomePageCarouselSlide):
    slides = ParentalKey('HomePage', related_name='slides')

class HomePageCard(models.Model):
    title = models.CharField(max_length=255, blank=True)
    description = RichTextField(blank=True, null=True)
    link_external = models.URLField("External link", blank=True)
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL,
    )
    feature_image = models.ForeignKey(
        PortalImage,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def url(self):
        if self.link_page and self.link_page.url:
            return self.link_page.url
        else:
            return self.link_external


    panels = [
        TitleFieldPanel('title'),
        FieldPanel('description'),
        FieldPanel('link_external'),
        PageChooserPanel('link_page'),
        FieldPanel('feature_image'),
    ]

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        else:
            return self.link_external

class HomePageCardSet(Orderable, HomePageCard):
    cards = ParentalKey('HomePage', related_name='cards')

class HomePage(Page):
    parent_page_types = []
    intro = RichTextField(blank=True)

    # def serve(self, request):
    #     # Randomize
    #     story = OceanStory.objects.live().exclude(display_home_page=False).order_by('?')[0]
    #     # Get First Always
    #     # story = [x for x in OceanStory.objects.live().exclude(display_home_page=False) if x.is_first_sibling()][0]
    #     return HttpResponseRedirect(story.url)

HomePage.content_panels = [
    FieldPanel('intro', classname="full"),
    InlinePanel('slides', label="Home Page Carousel Slides"),
    InlinePanel('cards', label="Home Page Content Cards"),

]
