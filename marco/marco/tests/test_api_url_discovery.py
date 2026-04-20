from django.test import SimpleTestCase
from django.urls import resolve


class ApiUrlDiscoveryTests(SimpleTestCase):
    """Ensure API routes from installed apps are auto-mounted under /api/."""

    def test_visualize_api_route_resolves(self):
        match = resolve('/api/bookmarks/')
        self.assertEqual(match.func.view_class.__name__, 'BookmarkListView')

    def test_drawing_api_route_resolves(self):
        match = resolve('/api/drawings/testuid123/')
        self.assertEqual(match.func.view_class.__name__, 'DrawingDeleteView')

    def test_mapgroups_api_route_resolves(self):
        match = resolve('/api/sharing-groups/')
        self.assertEqual(match.func.view_class.__name__, 'SharingGroupListView')
