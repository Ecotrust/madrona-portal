from wagtail.wagtailcore.models import Page

from django.http import HttpResponseRedirect
from portal.ocean_stories.models import OceanStory

class HomePage(Page):
    parent_page_types = []

    def serve(self, request):
        # Randomize
        # story = OceanStory.objects.live().exclude(display_home_page=False).order_by('?')[0]
        # Get First Always
        story = [x for x in OceanStory.objects.live().exclude(display_home_page=False) if x.is_first_sibling()][0]
        return HttpResponseRedirect(story.url)
