from django.db import models
from django.dispatch.dispatcher import receiver
from django.db.models.signals import pre_delete
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.conf import settings

if settings.WAGTAIL_VERSION > 3:
    from wagtail.models import Page
    from wagtail.fields import RichTextField
    from wagtail.search import index
    from wagtail.admin.panels import FieldPanel,MultiFieldPanel,TitleFieldPanel
    from wagtail.images.models import AbstractImage, AbstractRendition, Image
elif settings.WAGTAIL_VERSION > 1:
    from wagtail.core.models import Page
    from wagtail.core.fields import RichTextField
    from wagtail.search import index
    from wagtail.admin.edit_handlers import FieldPanel,MultiFieldPanel
    from wagtail.images.edit_handlers import ImageChooserPanel
    from wagtail.images.models import AbstractImage, AbstractRendition, Image
    TitleFieldPanel = FieldPanel
else:
    from wagtail.core.models import Page
    from wagtail.core.fields import RichTextField
    from wagtail.search import index
    from wagtail.admin.edit_handlers import FieldPanel,MultiFieldPanel
    from wagtail.images.edit_handlers import ImageChooserPanel
    from wagtail.images.models import AbstractImage, AbstractRendition, Image
    TitleFieldPanel = FieldPanel



# Portal defines its own custom image class to replace wagtailimages.Image,
# providing various additional data fields
# see https://github.com/torchbox/verdant-rca/blob/staging/django-verdant/rca/models.py
class PortalImage(AbstractImage):
    creator = models.CharField(max_length=255, blank=True)
    creator_URL = models.URLField(blank=True)

    search_fields = [x for x in AbstractImage.search_fields] + [
        index.SearchField('creator'),
    ]

    admin_form_fields = (
        *Image.admin_form_fields,
        'creator',
        'creator_URL'
    )

    @classmethod
    def creatable_subpage_models(cls):
        print(cls)

# Receive the pre_delete signal and delete the file associated with the model instance.
@receiver(pre_delete, sender=PortalImage)
def image_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.file.delete(False)

class PortalRendition(AbstractRendition):
    image = models.ForeignKey('PortalImage', related_name='renditions', on_delete=models.CASCADE)
    # Wagtail 1.8 deviates drastically from Wagtail 1.7. We need to support both for
    #   the automated migration from wagtail 1.3 to 2.9
    # TODO: Check if support needed for Wagtail 4.2 https://docs.wagtail.org/en/stable/releases/4.2.html#upgrade-considerations
    import wagtail
    if hasattr(wagtail, 'VERSION') and wagtail.VERSION[0] > 0 and (wagtail.VERSION[0] > 1 or wagtail.VERSION[1] > 7):
        class Meta:
            unique_together = (
                ('image', 'filter_spec', 'focal_point_key'),
            )
    else:
        class Meta:
            unique_together = (
                ('image', 'filter_spec', 'focal_point_key'),
            )

# Receive the pre_delete signal and delete the file associated with the model instance.
@receiver(pre_delete, sender=PortalRendition)
def rendition_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.file.delete(False)

class PageSection(models.Model):
    class Meta:
        abstract = True

    index_fields = ()

    def get_search_text(self):
        return '\n'.join(getattr(self, field) for field in self.index_fields)


class MediaItem(PageSection):
    media_position_choices = (
        ('left','left'),
        ('right','right'),
        ('full','full'),
    )
    media_image = models.ForeignKey(
        'base.PortalImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    media_embed_url = models.URLField(blank=True, help_text=(mark_safe("The URL to a "
        "video that you'd like to embed, e.g., https://vimeo.com/121095661.")))
    media_caption = models.CharField(max_length=255, blank=True)
    media_position = models.CharField(max_length=8, choices=media_position_choices, default=media_position_choices[0][0])

    index_fields = PageSection.index_fields + (
        'media_caption',
    )

    panels = [
        FieldPanel('media_image'),
        FieldPanel('media_embed_url'),
        FieldPanel('media_caption'),
        FieldPanel('media_position'),
    ]

    class Meta:
        abstract = True

    def clean(self):
        if self.media_image is not None and self.media_embed_url != '':
            raise ValidationError({'media_image': '', 'media_embed_url': 'Provide either an image or an embed URL, but not both.'})

class PageBase(Page):
    is_abstract = True
    class Meta:
        abstract = True

    description = RichTextField(blank=True, null=True)
    search_fields = [x for x in Page.search_fields] + [ # Inherit search_fields from Page
        index.SearchField('description'),
    ]

    def get_sections_search_text(self):
        return '\n'.join(section.get_search_text() for section in self.sections.all())

    content_panels = [
        MultiFieldPanel([
            TitleFieldPanel('title', classname="title"),
            FieldPanel('description'),
        ], 'Page')
    ]

    def portal_next_sibling(self):
        return self.get_next_siblings().live().first() or self.get_siblings().live().first()

    def portal_prev_sibling(self):
        return self.get_prev_siblings().live().first() or self.get_siblings().live().last()

class DetailPageBase(PageBase):
    is_abstract = True
    class Meta:
        abstract = True

    feature_image = models.ForeignKey(
        PortalImage,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    search_fields = (index.SearchField('description'),)

    subpage_types = []
    content_panels = PageBase.content_panels + [
        MultiFieldPanel([
            FieldPanel('feature_image'),
        ], 'Detail')
    ]
