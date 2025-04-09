from __future__ import absolute_import

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.

# Importing celery_app to ensure the Celery application is loaded
# when Django starts. This is necessary for shared_task to use this app.
from .celery import app as celery_app
__all__ = ('celery_app',)