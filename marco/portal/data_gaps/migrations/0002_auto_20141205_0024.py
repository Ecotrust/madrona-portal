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
        ('data_gaps', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='datagaps',
            name='description',
            field=wagtail_core_fields.RichTextField(default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='datagap',
            name='description',
            field=wagtail_core_fields.RichTextField(),
            preserve_default=True,
        ),
    ]
