from django import template
from django.conf import settings
from django.shortcuts import render
from django.template import RequestContext

if settings.WAGTAIL_VERSION > 1:
    from wagtail import models
    from wagtail.models import Page
    from wagtail.images.models import Image
    from wagtail.search.index import get_indexed_models, SearchField
    from wagtail.search.backends import get_search_backend
else:
    from wagtail import models
    from wagtail.models import Page
    from wagtail.images.models import Image
    from wagtail.search.index import get_indexed_models, SearchField
    from wagtail.search.backends import get_search_backend

from portal.base.models import PortalImage
from portal.ocean_stories.models import OceanStory, OceanStories
from portal.calendar.models import Event
from portal.news.models import News, Story

from data_manager.models import Layer, Theme

register = template.Library()

def search(request, template=settings.WAGTAILSEARCH_RESULTS_TEMPLATE, context = {}):
    query_string = request.GET.get('q', '')

    ocean_story_results = []
    calendar_news_results = []
    data_needs_results = []
    resources_results = []
    theme_results = []
    layer_results = []

    if len(query_string) >= 2:
        backend = get_search_backend()
        models = get_indexed_models()
        # remove unnecessary models
        for i in [Page, Image, PortalImage]:
            models.remove(i)

        # search wagtail pages
        for model in models:
            sfs = [x.field_name for x in model.search_fields if type(x) == SearchField]
            results = backend.search(query_string, model, fields=sfs)
            for item in results:
                if isinstance(item, (OceanStory, OceanStories)):
                    ocean_story_results.append(item)
                elif isinstance(item, (Event, News, Story)):
                    calendar_news_results.append(item)
                elif item.url and '/data-needs-and-priorities/' in item.url:
                    data_needs_results.append(item)
                elif item.url and '/resources/' in item.url:
                    resources_results.append(item)
            
        # search themes from data_catalog
        for theme in Theme.objects.filter(visible=True, display_name__icontains=query_string):
            theme_results.append(theme)

        # search layers from data_catalog
        layer_results.extend(Layer.objects.exclude(layer_type='placeholder').filter(themes__visible=True, name__icontains=query_string))

    sum_data_results = len(theme_results) + len(layer_results) + len(data_needs_results) + len(resources_results)

    context_response = context | {
        'ocean_story_results': ocean_story_results,
        'calendar_news_results': calendar_news_results,
        'data_needs_results': data_needs_results,
        'resources_results': resources_results,
        'theme_results': theme_results,
        'layer_results': layer_results,
        'sum_data_results': sum_data_results,
    }
    
    return render(request, template, context_response)
