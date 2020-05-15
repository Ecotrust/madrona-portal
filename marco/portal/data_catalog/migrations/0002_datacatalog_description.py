# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('data_catalog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='datacatalog',
            name='description',
            field=wagtail.core.fields.RichTextField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
