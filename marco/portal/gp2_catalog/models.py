from django.conf import settings
from django.db import models
from modelcluster.fields import ParentalKey

if settings.WAGTAIL_VERSION > 3:
    from wagtail.models import Page, Orderable
    from wagtail.fields import RichTextField, StreamField
    from wagtail import blocks
    from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel, InlinePanel, PageChooserPanel
    from wagtail.images.models import Image
    from wagtail.images.blocks import ImageChooserBlock
    from wagtail.search import index
else:
    from wagtail.models import Page, Orderable
    from wagtail.fields import RichTextField, StreamField
    from wagtail import blocks
    from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel, InlinePanel, PageChooserPanel
    from wagtail.images.models import Image
    from wagtail.images.edit_handlers import ImageChooserPanel
    from wagtail.images.blocks import ImageChooserBlock
    from wagtail.search import index


from portal.home.models import HomePage
from portal.base.models import PortalImage, DetailPageBase, PageBase, DetailPageBase, MediaItem
from portal.calendar.models import Calendar
from portal.news.models import News
from portal.ocean_stories.models import OceanStory, OceanStories
from portal.grid_pages.models import GridPage, GridPageDetail, GridPageSection, GridPageSectionBase
from django.conf import settings

class LinkStructValue(blocks.StructValue):
    def url(self):
        external_url = self.get('cta_link')
        page = self.get('cta_page')
        if external_url:
            return external_url
        elif page:
            return page.url

class BrickBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False)
    text = blocks.RichTextBlock(required=False)
    page = blocks.PageChooserBlock(label="page", required=False)
    external_url = blocks.URLBlock(label="external URL", required=False)
    photo = ImageChooserBlock(required=False)

    class Meta:
        icon = 'page'
        value_class = LinkStructValue

class CTARowDivider(blocks.StaticBlock):
    class Meta:
        icon = 'horizontalrule'
        label = 'Row divider'
        admin_text = 'Forces a new row to be created'

class CTAStreamBlock(blocks.StructBlock):
    cta_title = blocks.CharBlock(required=False)
    cta_content = blocks.RichTextBlock(required=False)
    cta_page = blocks.PageChooserBlock(label="page", required=False)
    cta_link = blocks.URLBlock(label="URL",required=False)
    # Width would be better as a CoiceBlock
    width = blocks.IntegerBlock(required=False,max_value=12,min_value=0,help_text="Number of columns to span out of 12 (e.g., input of 3 would mean give this a width of 3 out of the 12 (25%))")
    text_color = blocks.ChoiceBlock(choices=[
        ('white', 'White'),
        ('black', 'Black'),
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('red', 'Red'),
        ('purple', 'Purple'),
        ('grey', 'Grey'),
    ], icon='color_palette', required=False)
    background_color = blocks.ChoiceBlock(choices=[
        ('white', 'White'),
        ('black', 'Black'),
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('red', 'Red'),
        ('purple', 'Purple'),
        ('grey', 'Grey'),
    ], icon='color', required=False)
    background_image = ImageChooserBlock(required=False)

    class Meta:
        icon = 'form'
        value_class = LinkStructValue

class CTAPage(Page):
    if settings.WAGTAIL_VERSION > 3:
        body = StreamField(
            [
                ('item', CTAStreamBlock()),
                ('details', blocks.RichTextBlock()),
                ('row', CTARowDivider()),
            ],
            use_json_field=True
        )
    else:
        body = StreamField(
            [
                ('item', CTAStreamBlock()),
                ('details', blocks.RichTextBlock()),
                ('row', CTARowDivider()),
            ],
            use_json_field=True
        )

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]

    subpage_types = [
        'gp2_catalog.CTAPage',
        'grid_pages.GridPage',
        'calendar.Calendar',
        'news.News',
        'ocean_stories.OceanStories',
        'gp2_catalog.ConnectPage',
        'gp2_catalog.CatalogIframePage',
        'gp2_catalog.CatalogThemeGridPage',
        'pages.Page',
    ]
    
    page_ptr = models.OneToOneField(Page, parent_link=True, on_delete=models.CASCADE, related_name='gp2_CTAPage')

    def get_context(self, request):
        context = super().get_context(request)
        context['CATALOG_QUERY_ENDPOINT'] = settings.CATALOG_QUERY_ENDPOINT

        return context


class ConnectPage(Page):

    # Database fields

    grid_cta_one_title = models.CharField(max_length=255,null=True,blank=True)
    grid_cta_one = models.CharField(max_length=255,null=True,blank=True)
    grid_cta_two_title = models.CharField(max_length=255,null=True,blank=True)
    grid_cta_two = models.CharField(max_length=255,null=True,blank=True)
    grid_cta_three_title = models.CharField(max_length=255,null=True,blank=True)
    grid_cta_three = models.CharField(max_length=255,null=True,blank=True)

    body = RichTextField()
    body_image = models.ForeignKey(
        PortalImage,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    if settings.WAGTAIL_VERSION > 3:
        cta_list = StreamField(
            [
                ('connection', CTAStreamBlock()),
                ('details', blocks.RichTextBlock()),
            ],
            use_json_field=True
        )
    else:
        cta_list = StreamField(
            [
                ('connection', CTAStreamBlock()),
                ('details', blocks.RichTextBlock()),
            ],
            use_json_field=True
        )

    # Editor panels configuration

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('grid_cta_one_title'),
                FieldPanel('grid_cta_one'),
                FieldPanel('grid_cta_two_title'),
                FieldPanel('grid_cta_two'),
                FieldPanel('grid_cta_three_title'),
                FieldPanel('grid_cta_three'),
            ],
            heading="Top of page calls to action",
            classname="collapsible",
        ),
        FieldPanel('body'),
        FieldPanel('body_image'),
        FieldPanel('cta_list'),
    ]

    page_ptr = models.OneToOneField(Page, parent_link=True, on_delete=models.CASCADE, related_name='gp2_ConnectPage')


class CatalogIframePage(Page):
    # 255 is too short for much "DSL" queries to support GP2 + Elasticsearch
    # SO says <2000 is a good guideline: https://stackoverflow.com/a/417184/706797
    source = models.URLField(max_length=1999)

    content_panels = Page.content_panels + [
        FieldPanel('source')
    ]

    page_ptr = models.OneToOneField(Page, parent_link=True, on_delete=models.CASCADE, related_name='gp2_CatalogIframePage')

class CatalogThemeGridPage(GridPage):
    subpage_types = ['CatalogThemeGridPageDetail']
    gridpage_ptr = models.OneToOneField(GridPage, parent_link=True, on_delete=models.CASCADE, related_name='gp2_CatalogThemeGridPage')

    def get_detail_children(self):
        return CatalogThemeGridPageDetail.objects.child_of(self)

class CatalogThemeGridPageDetail(GridPageDetail):
    parent_page_types = ['CatalogThemeGridPage']
    theme = models.CharField(max_length=255, blank=True, null=True)

    search_fields = DetailPageBase.search_fields + (
        index.SearchField("description"),
        index.AutocompleteField("description"),
        index.FilterField("metric"),
        index.SearchField("theme"),
        index.AutocompleteField("theme"),
    )

    content_panels = DetailPageBase.content_panels + [
        FieldPanel('metric'),
        FieldPanel('theme')
    ]

    gridpagedetail_ptr = models.OneToOneField(GridPageDetail, parent_link=True, on_delete=models.CASCADE, related_name='gp2_CatalogThemeGridPageDetail')

gp2_catalog_appropriate_subpage_types = [
    # removes Data Catalog, and Data Gaps from defaultm adds gp2_catalog pages
    'calendar.Calendar',
    'gp2_catalog.CatalogIframePage',
    'gp2_catalog.CatalogThemeGridPage',
    'gp2_catalog.ConnectPage',
    'gp2_catalog.CTAPage',
    'grid_pages.GridPage',
    'news.News',
    'pages.Page',
    'ocean_stories.OceanStories',
]
Page.subpage_types = gp2_catalog_appropriate_subpage_types
# These should not be viable Root Pages
Calendar.parent_page_types = ['gp2_catalog.CTAPage','pages.Page',]
News.parent_page_types = ['gp2_catalog.CTAPage','pages.Page',]
