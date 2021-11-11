# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
if settings.WAGTAIL_VERSION > 1:
    import wagtail.core.fields as wagtail_core_fields
else:
    import wagtail.core.fields as wagtail_core_fields


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0002_page_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='description',
            field=wagtail_core_fields.RichTextField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
