# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
if settings.WAGTAIL_VERSION > 1:
    import wagtail.fields as wagtail_core_fields
else:
    import wagtail.fields as wagtail_core_fields


class Migration(migrations.Migration):

    dependencies = [
        ('calendar', '0005_auto_20150109_0053'),
    ]

    operations = [
        migrations.AddField(
            model_name='calendar',
            name='description',
            field=wagtail_core_fields.RichTextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='description',
            field=wagtail_core_fields.RichTextField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
