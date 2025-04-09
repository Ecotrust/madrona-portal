from django.conf import settings
from . import celery_app
from celery import shared_task

@shared_task
def start_dbwatch():
    import select
    import psycopg2
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
