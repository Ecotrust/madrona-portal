import sys
from django.apps import AppConfig

class MadronaPortalConfig(AppConfig):
    #TODO: Rename this module to 'madrona' or 'madrona_portal'
    name = 'marco'

    def ready(self):
        import threading
        if 'runserver' in sys.argv:
            thread = threading.Thread(target=self.start_dbwatch)
            thread.daemon = True
            thread.start()

    def start_dbwatch(self):
        import select
        import psycopg2
        from django.conf import settings
        from django.core.cache import cache
        from django.db import connection

        curs = connection.cursor()
        curs.execute("LISTEN {};".format(settings.DB_CHANNEL))

        # print("Waiting for notifications on channel '{}'".format(settings.DB_CHANNEL))
        while True:
            if select.select([connection.connection],[],[],5) == ([],[],[]):
                pass
            else:
                connection.connection.poll()
                while connection.connection.notifies:
                    notify = connection.connection.notifies.pop(0)
                    # print("Got NOTIFY:", notify.pid, notify.channel, notify.payload)
                    action = notify.payload.split(':')
                    if action[0] == 'deletecache':
                        key = action[1]
                        cache.delete(key)
                        # print("Deleted cache key:", key)