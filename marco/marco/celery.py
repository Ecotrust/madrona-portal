import os
from celery import Celery
from celery.signals import worker_ready
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marco.settings')

app = Celery('marco', include=['marco.tasks'])

# Pull Celery config from Django settings (keys prefixed with CELERY_).
# CELERY_BROKER_URL and CELERY_RESULT_BACKEND are set in settings.py from
# the CELERY_BROKER_URL / CELERY_RESULT_BACKEND env vars, or from the
# [CELERY] section of the project .ini config file.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@worker_ready.connect
def on_worker_ready(sender, **kwargs):
    """Start the long-running db-notify → cache-invalidation listener task
    once a Celery worker is live.  Keeping this out of AppConfig.ready()
    means Django can start without a Redis connection being required."""
    from marco.tasks import start_dbwatch
    start_dbwatch.delay()
