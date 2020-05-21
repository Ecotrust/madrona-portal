# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
if settings.WAGTAIL_VERSION > 1:
    import wagtail.core.fields as wagtail_core_fields
else:
    import wagtail.wagtailcore.fields as wagtail_core_fields


class Migration(migrations.Migration):

    dependencies = [
        ('ocean_stories', '0004_auto_20141219_2132'),
    ]

    operations = [
        migrations.AddField(
            model_name='oceanstories',
            name='description',
            field=wagtail_core_fields.RichTextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='oceanstory',
            name='description',
            field=wagtail_core_fields.RichTextField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
