from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from data_manager.models import *
from portal.base.models import PortalImage

# hack for POR-224, until POR-206
def wagtail_feature_image(self):
    image = PortalImage.objects.filter(tags__name__in=["theme"]).filter(tags__name__in=[self.name]).first()
    return image or None

Theme.wagtail_feature_image = wagtail_feature_image

def theme_query():
    return Theme.objects.filter(visible=True).exclude(name='companion').extra(
        select={
            'layer_count': "SELECT COUNT(*) FROM data_manager_layer_themes as mm LEFT JOIN data_manager_layer as l ON mm.layer_id = l.id WHERE mm.theme_id = data_manager_theme.id AND l.layer_type != 'placeholder'"
        }
    ).order_by('order')

def theme(request, theme_slug):
    from django.contrib.sites.shortcuts import get_current_site
    site = get_current_site(request)
    theme = get_object_or_404(theme_query(), name=theme_slug)
    template = 'data_catalog/theme.html'
    # layers = [x.dictCache(site.pk) for x in theme.layer_set.all().exclude(layer_type='placeholder').exclude(is_sublayer=True).order_by('order')]
    layers = []
    for layer in theme.layer_set.all().exclude(layer_type='placeholder').exclude(is_sublayer=True).order_by('order'):
        layers.append(layer.dictCache(site.pk))

    return render_to_response(
        template,
        {
            'theme': theme,
            'layers': layers,
        },
        context_instance=RequestContext(request)
    );
