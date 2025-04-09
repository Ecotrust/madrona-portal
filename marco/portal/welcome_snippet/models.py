from django.conf import settings
from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
import re
if settings.WAGTAIL_VERSION > 4:
    from wagtail.admin.panels import FieldPanel,InlinePanel,MultiFieldPanel,PageChooserPanel
    from wagtail.fields import RichTextField
    from wagtail.images.models import AbstractImage, AbstractRendition
    from wagtail.models import Orderable
    from wagtail.snippets.models import register_snippet
else:
    from wagtail.admin.edit_handlers import FieldPanel,InlinePanel,MultiFieldPanel,PageChooserPanel
    from wagtail.core.models import Orderable
    from wagtail.fields import RichTextField
    from wagtail.images.edit_handlers import ImageChooserPanel
    from wagtail.images.models import AbstractImage, AbstractRendition
    from wagtail.snippets.models import register_snippet


class WelcomePageEntry(Orderable):
    welcome_page = ParentalKey('WelcomePage', related_name='entries')
    title = models.CharField(null=True, blank=True, max_length=255)
    description = RichTextField(blank=True)
    url = models.CharField(null=True, blank=True, max_length=4096)
    show_divider_underneath = models.BooleanField(default=False)

    page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    media_image = models.ForeignKey(
        'base.PortalImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    panels = [
        FieldPanel('title'),
        FieldPanel('description'),
        FieldPanel('media_image'),
        FieldPanel('url'),
        PageChooserPanel('page'),
        FieldPanel('show_divider_underneath'),
    ]

    @property
    def destination(self):
        pattern = re.compile(r"https?://")
        try:
            external_url = pattern.match(self.url)
        except TypeError as e:
            external_url = False

        if self.page:
            return self.page.url
        elif external_url:
            return self.url
        elif self.url:
            return "/%s/" % self.url
        else:
            return "/"

    def external(self):
        pattern = re.compile(r"https?://")
        return pattern.match(self.destination)

    @property
    def text(self):
        return str(self)

    def __str__(self):
        if self.title:
            return self.title
        elif self.page:
            return self.page.title
        else:
            return ''

@register_snippet
class WelcomePage(ClusterableModel):
    title = models.CharField(max_length=255)
    body = RichTextField(null=True, blank=True)
    active = models.BooleanField(default=False)

    def __str__(self):
        return "%s%s" % (self.title, ' (active)' if self.active else '')

    def save(self, *args, **kwargs):
        if self.active:
            WelcomePage.objects.exclude(id=self.id).update(active=False)
        super(WelcomePage, self).save(*args, **kwargs)

WelcomePage.panels = [
    MultiFieldPanel([
        FieldPanel('title'),
        FieldPanel('body'),
        FieldPanel('active'),
    ]),
    InlinePanel('entries', label='Entries')
]
