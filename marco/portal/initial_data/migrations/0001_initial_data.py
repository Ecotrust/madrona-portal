# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
from wagtail.models import Locale
if settings.WAGTAIL_VERSION > 1:
    from wagtail.models import Page
else:
    from wagtail.models import Page

# def create_initial_data(apps, schema_editor):
#     home_page = Page.objects.get(url_path="/home/")
#     ContentType = apps.get_model('contenttypes.ContentType')
#
#     top_level_pages = [
#         {'app': 'ocean_stories', 'model_name': 'OceanStories', 'title': 'Ocean Stories', 'content_type': 'oceanstories', 'language':'en'},
#         {'app': 'calendar', 'model_name': 'Calendar', 'title': 'Calendar', 'content_type': 'calendar', 'language':'en'},
#         {'app': 'data_gaps', 'model_name': 'DataGaps', 'title': 'Data Gaps', 'content_type': 'datagaps', 'language':'en'},
#         {'app': 'data_catalog', 'model_name': 'DataCatalog', 'title': 'Data Catalog', 'content_type': 'datacatalog', 'language':'en'},
#     ]
#
#     for p in top_level_pages:
#         model = apps.get_model('%s.%s' % (p['app'], p['model_name']))
#         content_type, created = ContentType.objects.get_or_create(
#             model=p['content_type'], app_label=p['app'])
#         language = Locale.objects.get(language_code=p['language'])
#         home_page.add_child(instance=model(
#             title=p['title'],
#             live=False,
#             content_type=content_type,
#             locale_id=language.pk
#         ))


class Migration(migrations.Migration):
    dependencies = [
        ('ocean_stories', '0001_initial'),
        ('calendar', '0001_initial'),
        ('data_gaps', '0001_initial'),
        ('data_catalog', '0001_initial'),
        ('home', '0001_initial'),
    ]

    operations = [
        # migrations.RunPython(create_initial_data),
    ]
