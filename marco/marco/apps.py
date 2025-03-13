import sys
from django.apps import AppConfig

class MadronaPortalConfig(AppConfig):
    #TODO: Rename this module to 'madrona' or 'madrona_portal'
    name = 'marco'

    def ready(self):
        from .tasks import start_dbwatch
        watch_db = start_dbwatch.delay()