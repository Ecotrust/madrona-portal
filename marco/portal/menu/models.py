from django.utils.safestring import mark_safe
import re

from django.db import models
from django.conf import settings

from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey

if settings.WAGTAIL_VERSION > 4:
    from wagtail.models import Orderable
    from wagtail.admin.panels import FieldPanel,InlinePanel,MultiFieldPanel,PageChooserPanel,TitleFieldPanel
    from wagtail.snippets.models import register_snippet
elif settings.WAGTAIL_VERSION > 1:
    from wagtail.core.models import Orderable
    from wagtail.admin.edit_handlers import FieldPanel,InlinePanel,MultiFieldPanel,PageChooserPanel
    from wagtail.snippets.models import register_snippet
    TitleFieldPanel = FieldPanel
else:
    from wagtail.core.models import Orderable
    from wagtail.admin.edit_handlers import FieldPanel,InlinePanel,MultiFieldPanel,PageChooserPanel
    from wagtail.snippets.models import register_snippet
    TitleFieldPanel = FieldPanel


# The abstract model, complete with panels
class MenuEntryBase(models.Model):
    class Meta:
        abstract = True

    title = models.CharField(null=True, blank=True, max_length=255)
    url = models.CharField(null=True, blank=True, max_length=4096,
                           help_text=("Note: URLs starting with http:// will "
                                      "open in a new window."))
    show_divider_underneath = models.BooleanField(default=False)
    display_options = models.CharField(max_length=1, default='A', choices=(
        ('A', 'Always display'),
        ('I', 'Display only to logged-in users'),
        ('O', 'Display only to anonymous users'),
        ('S', 'Display only to staff and administrators')
    ))

    page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    panels = [
        TitleFieldPanel('title'),
        # PageChooserPanel('page'),
        FieldPanel('page'),
        FieldPanel('url'),
        FieldPanel('display_options'),
        FieldPanel('show_divider_underneath'),
    ]

    @property
    def destination(self):
        if self.page:
            return self.page.url
        else:
            return self.url

    def external(self):
        pattern = re.compile(r"https?://")
        return pattern.match(self.destination)

    @property
    def text(self):
        if self.title:
            return self.title
        elif self.page:
            return self.page.title
        else:
            return ""

    def __unicode__(self):
        return self.text

    def __str__(self):
        return self.text

# The real model which combines the abstract model, an
# Orderable helper class, and what amounts to a ForeignKey link
# to the model we want to add entries to (Menu)
class MenuEntry(Orderable, MenuEntryBase):
    menu = ParentalKey('Menu', related_name='entries')

@register_snippet
class Menu(ClusterableModel):
    class Meta:
        ordering = ('footer', 'order',)

    title = models.CharField(max_length=255)
    active = models.BooleanField(default=False, help_text=("To display this "
       "menu, check this box. "))
    is_user_menu = models.BooleanField(default=False, help_text=("If this menu "
        "is the User Menu, check this box."))
    footer = models.BooleanField(default=False, help_text=("Select to display "
       "this menu in the footer rather than in the nav bar. The footer has "
       "enough room for four menus."))
    order = models.PositiveSmallIntegerField(default=1, help_text=("The "
        "order that this menu appears. Lower numbers appear first."))

    panels = [
        MultiFieldPanel([
            TitleFieldPanel('title'),
            FieldPanel('active'),
            FieldPanel('is_user_menu'),
            FieldPanel('footer'),
            FieldPanel('order'),
        ]),
    ]

    def __unicode__(self):
        if self.active:
            active = ''
        else:
            active = '(inactive)'

        if self.footer:
            position = 'Footer'
        else:
            position = 'Navbar'

        s = '%s %d. <b>%s</b> %s' % (position, self.order, self.title, active)
        if not self.active:
            s = "<i style='color:#999'>%s</i>" % s

        return mark_safe(s)

    def __str__(self):
        if self.active:
            active = ''
        else:
            active = '(inactive)'

        if self.footer:
            position = 'Footer'
        else:
            position = 'Navbar'

        s = '%s %d. <b>%s</b> %s' % (position, self.order, self.title, active)
        if not self.active:
            s = "<i style='color:#999'>%s</i>" % s

        return mark_safe(s)

# TODO suppport lower versions of wagtail
# Menu.panels.append(InlinePanel('entries', label="Entries" ))
# Menu.panels.append(FieldPanel('entries'))
