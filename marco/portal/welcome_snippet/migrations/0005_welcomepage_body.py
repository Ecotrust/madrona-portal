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
        ('welcome_snippet', '0004_auto_20150502_1649'),
    ]

    operations = [
        migrations.AddField(
            model_name='welcomepage',
            name='body',
            field=wagtail_core_fields.RichTextField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
