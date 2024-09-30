from django.shortcuts import get_object_or_404, render
from django.template import RequestContext
from data_manager import models as data_manager_models
from layers.models import Theme, Layer
from portal.base.models import PortalImage

# hack for POR-224, until POR-206
def wagtail_feature_image(self):
    image = PortalImage.objects.filter(tags__name__in=["theme"]).filter(tags__name__in=[self.name]).first()
    return image or None

Theme.wagtail_feature_image = wagtail_feature_image

def theme_query():
    return Theme.objects.filter(is_visible=True).exclude(name='companion').order_by('order')


def theme(request, theme_slug):
    from django.contrib.sites.shortcuts import get_current_site
    site = get_current_site(request)
    theme = get_object_or_404(theme_query(), name=theme_slug)
    template = 'data_catalog/theme.html'
    context = {
        'theme': theme,
        'children': theme.shortDict()['children'],
    }

    return render(request, template, context)
