from collections import OrderedDict
from django.conf import settings
try:
    from itertools import zip_longest
except Exception as e:
    # Py2 compatibility
    from itertools import izip_longest as zip_longest
import json
from data_manager.models import Layer

try:
    import urlparse as parse
except ImportError:
    from urllib import parse

from django.db import models
from django.core.exceptions import ValidationError
from modelcluster.fields import ParentalKey
from portal.base.models import PageBase, DetailPageBase, MediaItem

if settings.WAGTAIL_VERSION > 3:
    from wagtail.models import Orderable
    from wagtail.fields import StreamField
    from wagtail.search import index
    from wagtail.admin.panels import FieldPanel,InlinePanel,MultiFieldPanel,TitleFieldPanel
    from wagtail.blocks import RichTextBlock, RawHTMLBlock    
elif settings.WAGTAIL_VERSION > 1:
    from wagtail.models import Orderable
    from wagtail.fields import StreamField
    from wagtail.search import index
    from wagtail.admin.panels import FieldPanel,InlinePanel,MultiFieldPanel,StreamFieldPanel
    from wagtail.blocks import RichTextBlock, RawHTMLBlock
    TitleFieldPanel = FieldPanel
else:
    from wagtail.models import Orderable
    from wagtail.fields import StreamField
    from wagtail.search import index
    from wagtail.admin.panels import FieldPanel,InlinePanel,MultiFieldPanel,StreamFieldPanel
    from wagtail.blocks import RichTextBlock, RawHTMLBlock
    TitleFieldPanel = FieldPanel

def grouper(iterable, n, fillvalue=None):
    """Collect data into fixed-length chunks or blocks.
    See: https://docs.python.org/2/library/itertools.html#recipes
    """
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)

# The abstract model for ocean story sections, complete with panels
class OceanStorySectionBase(MediaItem):
    title = models.CharField(max_length=255, blank=True)
    if settings.WAGTAIL_VERSION > 3:
        body = StreamField(
            [
                ('rich_text', RichTextBlock()),
                ('raw_html', RawHTMLBlock()),
            ],
            null=True,
            blank=True,
            use_json_field=True,
        )
    else:
        body = StreamField(
            [
                ('rich_text', RichTextBlock()),
                ('raw_html', RawHTMLBlock()),
            ],
            null=True,
            blank=True,
        )
    map_state = models.TextField()
    map_legend = models.BooleanField(default=False, help_text=("Check to "
       "display the map's legend to the right of the the section text."))

    panels = [
        TitleFieldPanel('title'),
        MultiFieldPanel(MediaItem.panels, "media"),
        FieldPanel('body'),
        FieldPanel('map_state'),
        FieldPanel('map_legend'),
    ]

    index_fields = MediaItem.index_fields + (
        'title',
        'body',
    )

    class Meta:
        abstract = True

    def parsed_map_state(self):
        if not self.map_state.startswith("http"):
            return json.loads(self.map_state)

        o = parse.urlparse(self.map_state)
        data_layers = {}
        params = parse.parse_qs(o.fragment)

        dls = params.pop('dls[]', [])

        # Track layer order so we can enforce it in legends and maps later.
        layer_ids = []

        # dls[]=[true,1,54,true,0.5,42,...] ->
        # dls[] = [(true, 1, 54), (true, 0.5, 42), ...]
        for visible, opacity, layer_id in grouper(dls, 3):
            layer_ids.append(layer_id)
            visible = visible.lower() in ('true', '1')
            opacity = float(opacity)
            try:
                int(layer_id)
            except ValueError:
                # IDs that can't be converted to integers are features, e.g.,
                # 'drawing_aoi_13', which can't be displayed on ocean story
                # maps, so just continue.
                continue

            layer = Layer.objects.filter(id=layer_id)
            layer = layer.values('legend', 'show_legend', 'name', 'layer_type', 'url', 'arcgis_layers')

            # layer ID must be a string here
            data_layers[layer_id] = {}
            if not layer:
                continue
            layer = layer[0]

            data_layers[layer_id]['id'] = layer_id
            data_layers[layer_id]['name'] = layer['name']
            if layer['show_legend']:
                data_layers[layer_id]['legend'] = layer['legend']
            else:
                data_layers[layer_id]['legend'] = False
            data_layers[layer_id]['legend_source'] = 'img'
            data_layers[layer_id]['arcgis_layers'] = layer['arcgis_layers']
            if (layer['show_legend'] and (layer['legend'] == u'' or layer['legend'] == None)) and layer['layer_type'] == 'ArcRest' and '/export' in layer['url']:
                data_layers[layer_id]['legend_source'] = 'url'
                data_layers[layer_id]['legend'] = "%s" % layer['url'].split('/export')[0]
            if (layer['show_legend'] and (layer['legend'] == u'' or layer['legend'] == None)) and layer['layer_type'] == 'ArcFeatureServer' and '/FeatureServer' in layer['url']:
                data_layers[layer_id]['legend_source'] = 'arc_feature_service'
                data_layers[layer_id]['legend'] = "%s/%s?f=json" % (layer['url'], layer['arcgis_layers'])

        # Layers are presented in the URL in stack order (FILO). 
        # Collect the order, then enforce the layers to be stored in reverse order.
        ordered_data_layers = OrderedDict()
        layer_ids.reverse()
        for l_id in layer_ids:
            ordered_data_layers[l_id] = data_layers[l_id]

        s = {
            'view': {
                'center': (params.get('x', [-73.24])[0],
                           params.get('y', [38.93])[0]),
                'zoom': params.get('z', [7])[0],
            },
            'url': self.map_state,
            'baseLayer': params.get('basemap', ['Ocean'])[0],
            'dataLayers': ordered_data_layers,
            'layerOrder': layer_ids
        }

        for lyr in s['dataLayers'].keys(): print(lyr)


        return s

    def clean(self):
        super(OceanStorySectionBase, self).clean()
        try:
            self.parsed_map_state()
        except Exception as e:
            raise ValidationError({'map_state': 'Invalid map state'})

# The real model which combines the abstract model, an
# Orderable helper class, and what amounts to a ForeignKey link
# to the model we want to add sections to (OceanStory)
class OceanStorySection(Orderable, OceanStorySectionBase):
    page = ParentalKey('OceanStory', related_name='sections')

class OceanStories(PageBase):
    subpage_types = ['OceanStory']

    search_fields = (index.SearchField('description'),)

    def get_detail_children(self):
        return OceanStory.objects.child_of(self)

class OceanStory(DetailPageBase):
    parent_page_types = ['OceanStories']

    display_home_page = models.BooleanField(default=True, help_text=("Check to "
       "display this ocean story on the home page"))
    hook = models.CharField(max_length=256, blank=True, null=True)
    explore_title = models.CharField(max_length=256, blank=True, null=True)
    explore_url = models.URLField(max_length=4096, blank=True, null=True)

    search_fields = DetailPageBase.search_fields + (
        index.SearchField('description'),
        index.SearchField('hook'),
        index.SearchField('get_sections_search_text'),
    )

    def get_context(self, request):
        import importlib
        context = super(OceanStory, self).get_context(request)
        if importlib.util.find_spec("visualize") and hasattr(settings, 'MAP_LIBRARY') and settings.MAP_LIBRARY:
            # Use mp-visualize code and set map library
            context['MAP_LIBRARY'] = settings.MAP_LIBRARY
            context['ARCGIS_API_KEY'] = settings.ARCGIS_API_KEY
            if hasattr(settings, 'PROJECT_REGION'):
                context['REGION'] = settings.PROJECT_REGION
            else:
                context['REGION'] = {
                    'name': 'Mid Atlantic',
                    'init_zoom': 7,
                    'init_lat': 39,
                    'init_lon': -74,
                    'srid': 4326,
                    'map': 'ocean'
                }
        else:
            # use old hard-coded pre-OL3 code.
            context['MAP_LIBRARY'] = False
            context['ARCGIS_API_KEY'] = settings.ARCGIS_API_KEY
        return context

    def as_json(self):
        # try:
        o = {'sections': [s.parsed_map_state() for s in self.sections.all()]}
        # except:
        # o = {'sections': []}
        return json.dumps(o)

    def get_siblings(self, inclusive=True):
        return self.__class__.objects.sibling_of(self, inclusive)

    def os_next_sibling(self):
        return self.get_next_siblings().live().filter(display_home_page=True).first() or \
            self.get_siblings().live().filter(display_home_page=True).first()

    def os_prev_sibling(self):
        return self.get_prev_siblings().live().filter(display_home_page=True).first() or \
            self.get_siblings().live().filter(display_home_page=True).last()

    def is_first_sibling(self):
        return len(self.get_prev_siblings().live().filter(display_home_page=True)) == 0


OceanStory.content_panels = DetailPageBase.content_panels + [
    FieldPanel('display_home_page'),
    MultiFieldPanel([FieldPanel('hook'), FieldPanel('explore_title'), FieldPanel('explore_url')], "Map overlay"),
    InlinePanel('sections', label="Sections" ),
]
