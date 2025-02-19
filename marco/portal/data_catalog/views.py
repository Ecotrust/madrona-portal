from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import OuterRef, Subquery, Exists
from django.shortcuts import get_object_or_404, render
from django.template import RequestContext
from data_manager import models as data_manager_models
from layers.models import Theme, Layer, ChildOrder
from portal.base.models import PortalImage

# hack for POR-224, until POR-206
def wagtail_feature_image(self):
    image = PortalImage.objects.filter(tags__name__in=["theme"]).filter(tags__name__in=[self.name]).first()
    return image or None

Theme.wagtail_feature_image = wagtail_feature_image

def theme_query(site):
    child_orders = ChildOrder.objects.filter(object_id=OuterRef('pk'), content_type=ContentType.objects.get_for_model(Theme))
    
    return Theme.objects.filter(
        is_visible=True,
        site=site
    ).annotate(
        has_parent=Exists(child_orders)
    ).exclude(
        name='companion'
    ).filter(
        has_parent=False  
    ).order_by('order')


def theme(request, theme_slug):
    site = get_current_site(request)
    theme = get_object_or_404(theme_query(site), name=theme_slug)
    template = 'data_catalog/theme.html'
    context = {
        'theme': theme,
        'children': theme.shortDict(site=site)['children'],
    }

    return render(request, template, context)
